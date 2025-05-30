import os
import aiosqlite
import asyncio
from typing import Optional, List, Any
from contextlib import asynccontextmanager
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from .wis.c4a_commen.basemodels import CrawlResult
from .tools.general_utils import get_logger
from .wis.utils import ensure_content_dirs, generate_content_hash
from datetime import datetime, timedelta


base_directory = os.path.join(".", os.getenv("PROJECT_DIR", "work_dir"))
os.makedirs(base_directory, exist_ok=True)
wis_logger = get_logger(base_directory, "wiseflow_info_scraper")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "pb", "pb_data")


@dataclass
class ContentMapping:
    """内容类型映射配置"""
    field_name: str
    store_as_file: bool      # True表示存储为文件, False表示直接存DB
    content_type_for_file: Optional[str] = None # 如果 store_as_file=True, 这是文件类型/目录名
    is_json_content: bool = False # 内容本身是否为JSON (影响序列化/反序列化)


class AsyncDatabaseManager:
    """优化后的异步数据库管理器"""
    
    # 内容字段映射配置
    CONTENT_MAPPINGS = [
        # 文件存储的字段
        ContentMapping("html", store_as_file=True, content_type_for_file="html"),
        ContentMapping("markdown", store_as_file=True, content_type_for_file="markdown"),
        ContentMapping("screenshot", store_as_file=True, content_type_for_file="screenshots"),
        # 数据库存储的JSON字段
        ContentMapping("link_dict", store_as_file=True, content_type_for_file="link_dict", is_json_content=True),
        ContentMapping("metadata", store_as_file=False, is_json_content=True),
        ContentMapping("downloaded_files", store_as_file=False, is_json_content=True),
    ]
    
    def __init__(self, pool_size: int = 5, max_retries: int = 3):
        self.content_paths = ensure_content_dirs(os.path.join(base_directory, ".wis"))
        self.db_path = os.path.join(DB_PATH, "data.db")
        self.max_retries = max_retries
        
        # 真正的连接池
        self._connection_pool: List[aiosqlite.Connection] = []
        self._pool_size = pool_size
        self._available_connections = asyncio.Queue(maxsize=pool_size)
        self._pool_initialized = False
        self._init_lock = asyncio.Lock()
        
        # 文件I/O线程池
        self._file_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="db_file_io")
        
        # 内容字段映射字典，提高查找效率
        self._content_field_map = {cm.field_name: cm for cm in self.CONTENT_MAPPINGS}
        self._file_storage_fields = {cm.field_name: cm for cm in self.CONTENT_MAPPINGS if cm.store_as_file}
        self._db_storage_json_fields = {cm.field_name: cm for cm in self.CONTENT_MAPPINGS if not cm.store_as_file and cm.is_json_content}

    async def initialize(self):
        """初始化数据库和连接池"""
        async with self._init_lock:
            if self._pool_initialized:
                return
                
            try:
                wis_logger.debug("Initializing optimized database manager")
                
                # 确保数据库表存在
                await self._init_db_schema()
                
                # 初始化真正的连接池
                await self._init_connection_pool()
                
                self._pool_initialized = True
                wis_logger.debug("Database manager initialized successfully")
                
            except Exception as e:
                wis_logger.error(f"Database initialization failed: {str(e)}")
                raise

    async def _init_db_schema(self):
        """初始化数据库模式，包含表结构校验和缺失列自动补充"""
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            # 定义期望的表结构
            expected_columns = {
                'url': 'TEXT PRIMARY KEY',
                'html': 'TEXT',
                'markdown': 'TEXT DEFAULT ""',
                'link_dict': 'TEXT DEFAULT ""',
                'metadata': 'TEXT DEFAULT "{}"',
                'screenshot': 'TEXT DEFAULT ""',
                'downloaded_files': 'TEXT DEFAULT "[]"',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # 首先创建表（如果不存在）
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS crawled_data (
                    {', '.join([f'{col} {definition}' for col, definition in expected_columns.items()])}
                )
            """
            await db.execute(create_table_sql)
            
            # 检查表是否存在
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='crawled_data'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if table_exists:
                # 获取当前表的列信息
                async with db.execute("PRAGMA table_info(crawled_data)") as cursor:
                    current_columns_info = await cursor.fetchall()
                
                # 构建当前列的详细信息 {列名: (类型, 是否非空, 默认值, 是否主键)}
                current_columns = {}
                for row in current_columns_info:
                    col_name = row[1]
                    col_type = row[2]
                    current_columns[col_name] = {
                        'type': col_type,
                        'not_null': bool(row[3]),
                        'default_value': row[4],
                        'is_primary_key': bool(row[5])
                    }
                
                expected_column_names = set(expected_columns.keys())
                current_column_names = set(current_columns.keys())
                
                # 找出缺失的列
                missing_columns = expected_column_names - current_column_names
                
                if missing_columns:
                    wis_logger.info(f"Found missing columns in crawled_data table: {missing_columns}")
                    
                    # 添加缺失的列
                    for column_name in missing_columns:
                        column_definition = expected_columns[column_name]
                        # 移除PRIMARY KEY约束（只能在CREATE TABLE时使用）
                        if 'PRIMARY KEY' in column_definition:
                            column_definition = column_definition.replace(' PRIMARY KEY', '')
                        
                        try:
                            alter_sql = f"ALTER TABLE crawled_data ADD COLUMN {column_name} {column_definition}"
                            await db.execute(alter_sql)
                            wis_logger.info(f"Successfully added column '{column_name}' to crawled_data table")
                        except Exception as e:
                            wis_logger.error(f"Failed to add column '{column_name}': {str(e)}")
                else:
                    wis_logger.debug("All expected columns exist in crawled_data table")
                
                # 检查现有列的类型是否匹配期望
                type_mismatches = []
                for col_name in current_column_names & expected_column_names:
                    expected_def = expected_columns[col_name]
                    # 提取期望的类型（去掉约束和默认值）
                    expected_type = expected_def.split()[0]  # 取第一个词作为类型
                    current_type = current_columns[col_name]['type']
                    
                    # SQLite类型比较（不区分大小写）
                    if expected_type.upper() != current_type.upper():
                        type_mismatches.append({
                            'column': col_name,
                            'expected': expected_type,
                            'current': current_type
                        })
                
                if type_mismatches:
                    wis_logger.warning("Found column type mismatches (SQLite is flexible with types, but this may indicate schema evolution):")
                    for mismatch in type_mismatches:
                        wis_logger.warning(f"  Column '{mismatch['column']}': expected {mismatch['expected']}, found {mismatch['current']}")
            
            # 添加索引提高查询性能
            indexes = [
                ("idx_crawled_data_updated_at", "updated_at"),
                ("idx_crawled_data_created_at", "created_at")
            ]
            
            for index_name, column_name in indexes:
                try:
                    await db.execute(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON crawled_data({column_name})
                    """)
                except Exception as e:
                    wis_logger.warning(f"Failed to create index {index_name}: {str(e)}")
            
            await db.commit()
            wis_logger.debug("Database schema initialization completed")

    async def _init_connection_pool(self):
        """初始化真正的连接池"""
        for _ in range(self._pool_size):
            conn = await aiosqlite.connect(self.db_path, timeout=30.0)
            await conn.execute("PRAGMA journal_mode = WAL")
            await conn.execute("PRAGMA busy_timeout = 5000")
            await conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            await conn.execute("PRAGMA synchronous = NORMAL")
            
            self._connection_pool.append(conn)
            await self._available_connections.put(conn)

    @asynccontextmanager
    async def get_connection(self):
        """获取连接池中的连接"""
        if not self._pool_initialized:
            await self.initialize()
            
        # 从池中获取连接
        conn = await self._available_connections.get()
        try:
            yield conn
        finally:
            # 归还连接到池中
            await self._available_connections.put(conn)

    async def execute_with_retry(self, operation, *args):
        """带重试的数据库操作执行"""
        for attempt in range(self.max_retries):
            try:
                async with self.get_connection() as db:
                    result = await operation(db, *args)
                    await db.commit()
                    return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    wis_logger.error(f"Operation failed after {self.max_retries} attempts: {str(e)}")
                    raise
                await asyncio.sleep(0.5 * (2 ** attempt))  # 指数退避

    async def cache_url(self, result: CrawlResult):
        """缓存URL数据 - 优化版本"""
        # 如果有重定向URL，使用重定向URL作为主键
        cache_url = result.redirected_url if result.redirected_url else result.url
        if not cache_url:
            return
        
        # 并发存储需要文件存储的内容
        content_tasks = []
        for field_name, mapping in self._file_storage_fields.items():
            if hasattr(result, field_name):
                content = getattr(result, field_name)
                # 处理空值和None值的统一化
                if field_name == "markdown":
                    content = content or ""
                elif field_name == "link_dict":
                    content = content or {}
                
                if content:
                    task = self._store_content_async(content, mapping.content_type_for_file)
                    content_tasks.append((field_name, task))
        
        # 等待所有文件存储完成
        content_hashes = {}
        if content_tasks:
            results = await asyncio.gather(*[task for _, task in content_tasks], return_exceptions=True)
            for (field_name, _), result_hash in zip(content_tasks, results):
                if isinstance(result_hash, Exception):
                    wis_logger.error(f"Failed to store {field_name}: {result_hash}")
                    content_hashes[field_name] = ""
                else:
                    content_hashes[field_name] = result_hash or ""
        
        # 数据库操作
        async def _cache(db):
            await db.execute("""
                INSERT INTO crawled_data (
                    url, html, markdown,
                    link_dict, metadata, screenshot, 
                    downloaded_files, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(url) DO UPDATE SET
                    html = excluded.html,
                    markdown = excluded.markdown,
                    link_dict = excluded.link_dict,
                    metadata = excluded.metadata,
                    screenshot = excluded.screenshot,
                    downloaded_files = excluded.downloaded_files,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                cache_url,
                content_hashes.get("html", ""),
                content_hashes.get("markdown", ""),
                content_hashes.get("link_dict", ""),
                self._serialize_json(result.metadata),
                content_hashes.get("screenshot", ""),
                self._serialize_json(result.downloaded_files, default_as_list=True)
            ))

        try:
            await self.execute_with_retry(_cache)
        except Exception as e:
            wis_logger.error(f"Error caching URL {cache_url}: {str(e)}")

    async def get_cached_url(self, url: str, days_threshold: int = 30) -> Optional[CrawlResult]:
        """获取缓存的URL数据 - 优化版本"""
        async def _get(db):
            async with db.execute(
                "SELECT * FROM crawled_data WHERE url = ?", (url,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                # 构建行数据字典
                columns = [desc[0] for desc in cursor.description]
                # Check if the cache is expired based on the updated_at timestamp
                try:
                    updated_at_index = columns.index('updated_at')
                    updated_at_str = row[updated_at_index]
                    if self.is_cache_expired(updated_at_str, days_threshold):
                        wis_logger.debug(f"Cache for {url} expired (>{days_threshold} days). Returning None.")
                        return None
                except ValueError:
                    # 'updated_at' column not found, treat as not expired (or log a warning)
                    # This case should ideally not happen with schema initialization, but as a fallback
                    wis_logger.warning("Column 'updated_at' not found in crawled_data table. Cannot check cache expiration.")
                    return None
                except Exception as e:
                    # Handle potential errors during date parsing or comparison
                    wis_logger.error(f"Error checking cache expiration for {url}: {str(e)}")
                    return None

                row_dict = dict(zip(columns, row))
                
                # 并发加载文件存储的内容
                load_tasks = []
                for field_name, mapping in self._file_storage_fields.items():
                    if field_name in row_dict and row_dict[field_name]:
                        task = self._load_content_async(row_dict[field_name], mapping.content_type_for_file)
                        load_tasks.append((field_name, mapping, task))
                
                # 等待所有文件加载完成
                if load_tasks:
                    results = await asyncio.gather(*[task for _, _, task in load_tasks], return_exceptions=True)
                    for (field_name, mapping, _), content in zip(load_tasks, results):
                        if isinstance(content, Exception):
                            wis_logger.error(f"Failed to load {field_name}: {content}")
                            if mapping.is_json_content:
                                if field_name == "link_dict":
                                    row_dict[field_name] = {}
                                else:
                                    row_dict[field_name] = ""
                            else:
                                row_dict[field_name] = ""
                        else:
                            if mapping.is_json_content:
                                deserialized = self._deserialize_json(content)
                                if field_name == "link_dict" and not deserialized:
                                    row_dict[field_name] = {}
                                else:
                                    row_dict[field_name] = deserialized
                            else:
                                row_dict[field_name] = content or ""
                
                # If link_dict is an empty string (default from DB or failed load of empty content),
                # ensure it's an empty dictionary for CrawlResult.
                if row_dict.get("link_dict") == "":
                    row_dict["link_dict"] = {}

                if "downloaded_files" in row_dict:
                    row_dict["downloaded_files"] = self._deserialize_json(row_dict["downloaded_files"], default_as_list=True)
                
                if "metadata" in row_dict:
                    row_dict["metadata"] = self._deserialize_json(row_dict["metadata"], default_as_list=False)
                
                # 过滤并构建CrawlResult
                valid_fields = CrawlResult.__annotations__.keys()
                # print(f"row_dict: {row_dict}")
                filtered_dict = {k: v for k, v in row_dict.items() if k in valid_fields}
                filtered_dict["success"] = True
                return CrawlResult(**filtered_dict)

        try:
            return await self.execute_with_retry(_get)
        except Exception as e:
            wis_logger.error(f"Error retrieving cached URL {url}: {str(e)}")
            return None
    
    def is_cache_expired(self, updated_at: str, days_threshold: int = 30) -> bool:
        """
        检查缓存是否过期
        
        Args:
            updated_at: 更新时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
            days_threshold: 过期天数阈值，默认30天
            
        Returns:
            bool: True表示已过期，False表示未过期
        """
        if not updated_at:
            return True
            
        try:
            # 解析时间字符串
            cache_time = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            
            # 计算时间差
            time_diff = current_time - cache_time
            
            # 检查是否超过阈值
            return time_diff > timedelta(days=days_threshold)
            
        except (ValueError, TypeError) as e:
            # 如果时间格式解析失败，认为缓存已过期
            return True

    async def _store_content_async(self, content: Any, content_type: str) -> str:
        """异步存储内容到文件系统"""
        if not content:
            return ""
            
        # 处理不同类型的内容
        if isinstance(content, dict) or isinstance(content, list):
            content_str = json.dumps(content, ensure_ascii=False)
        else:
            content_str = str(content)
            
        content_hash = generate_content_hash(content_str)
        file_path = os.path.join(self.content_paths[content_type], content_hash)
        
        # 异步检查文件是否已存在（避免重复写入）
        loop = asyncio.get_event_loop()
        file_exists = await loop.run_in_executor(
            self._file_executor,
            os.path.exists,
            file_path
        )
        
        if not file_exists:
            # 使用线程池进行文件I/O操作
            await loop.run_in_executor(
                self._file_executor,
                self._write_file_sync,
                file_path,
                content_str
            )
        
        return content_hash

    async def _load_content_async(self, content_hash: str, content_type: str) -> Optional[str]:
        """异步从文件系统加载内容"""
        if not content_hash:
            return None
            
        file_path = os.path.join(self.content_paths[content_type], content_hash)
        
        # 使用线程池进行文件I/O操作
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                self._file_executor,
                self._read_file_sync,
                file_path
            )
        except Exception as e:
            wis_logger.error(f"Failed to load content from {file_path}: {e}")
            return None

    def _write_file_sync(self, file_path: str, content: str):
        """同步写文件（在线程池中执行）"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _read_file_sync(self, file_path: str) -> str:
        """同步读文件（在线程池中执行）"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _serialize_json(self, data: Any, default_as_list: bool = False) -> str:
        """序列化JSON数据"""
        if data is None:
            return "[]" if default_as_list else "{}"
        try:
            return json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError):
            return "[]" if default_as_list else "{}"

    def _deserialize_json(self, data: str, default_as_list: bool = False) -> Any:
        """反序列化JSON数据"""
        if not data:
            return [] if default_as_list else {}
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return [] if default_as_list else {}

    async def get_total_count(self) -> int:
        """获取缓存总数"""
        async def _count(db):
            async with db.execute("SELECT COUNT(*) FROM crawled_data") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

        try:
            return await self.execute_with_retry(_count)
        except Exception as e:
            wis_logger.error(f"Error getting total count: {str(e)}")
            return 0

    async def clear_db(self):
        """清空数据库"""
        async def _clear(db):
            await db.execute("DROP TABLE IF EXISTS crawled_data")
        try:
            await self.execute_with_retry(_clear)
            wis_logger.debug("table crawled_data dropped successfully")
        except Exception as e:
            wis_logger.error(f"Error clearing database: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        # 关闭所有连接
        for conn in self._connection_pool:
            await conn.close()
        self._connection_pool.clear()
        
        # 关闭线程池
        self._file_executor.shutdown(wait=True)


# 创建优化后的单例实例
db_manager = AsyncDatabaseManager()

async def init_database():
    """
    应用启动时调用此函数来预初始化数据库
    这样可以避免第一次数据库操作时的初始化延迟
    """
    try:
        await db_manager.initialize()
        wis_logger.debug("Database pre-initialized successfully")
    except Exception as e:
        wis_logger.error(f"Database pre-initialization failed: {e}")
        raise

async def cleanup_database():
    """
    应用关闭时调用此函数来清理数据库资源
    """
    try:
        await db_manager.cleanup()
        wis_logger.debug("Database cleanup completed")
    except Exception as e:
        wis_logger.error(f"Database cleanup failed: {e}")
