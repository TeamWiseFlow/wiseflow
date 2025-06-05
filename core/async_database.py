import os
import aiosqlite
import asyncio
import uuid
from typing import Optional, List, Any
from contextlib import asynccontextmanager
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from wis.basemodels import CrawlResult
from wis.utils import ensure_content_dirs, generate_content_hash
from datetime import datetime, timedelta, timezone
from async_logger import base_directory, wis_logger


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "pb", "pb_data")


@dataclass
class ContentMapping:
    """内容类型映射配置"""
    field_name: str
    content_type_for_file: str # 文件类型/目录名
    is_json_content: bool = False # 内容本身是否为JSON (影响序列化/反序列化)


class AsyncDatabaseManager:
    """优化后的异步数据库管理器"""
    
    # 内容字段映射配置 - 所有字段都存储为文件
    CONTENT_MAPPINGS = [
        ContentMapping("html", content_type_for_file="html"),
        ContentMapping("markdown", content_type_for_file="markdown"),
        ContentMapping("screenshot", content_type_for_file="screenshots"),
        ContentMapping("cleaned_html", content_type_for_file="cleaned_html"),
        ContentMapping("link_dict", content_type_for_file="link_dict", is_json_content=True),
    ]

    # 表结构定义
    TABLE_SCHEMAS = {
        'crawled_data': {
            'id': 'TEXT PRIMARY KEY',
            'url': 'TEXT NOT NULL',
            'html': 'TEXT DEFAULT ""',
            'markdown': 'TEXT DEFAULT ""',
            'link_dict': 'TEXT DEFAULT ""',
            'cleaned_html': 'TEXT DEFAULT ""',
            'screenshot': 'TEXT DEFAULT ""',
            'downloaded_files': 'JSON DEFAULT "[]"',
            'title': 'TEXT DEFAULT ""',
            'author': 'TEXT DEFAULT ""',
            'publish_date': 'TEXT DEFAULT ""',
            'updated': 'TEXT'  # 注意：PocketBase 中实际为 datetime 类型
        },
        'infos': {
            'id': 'TEXT PRIMARY KEY',
            'content': 'TEXT NOT NULL',
            'focuspoint': 'TEXT',
            'source': 'TEXT',
            'references': 'TEXT DEFAULT ""',
            'updated': 'TEXT'  # 注意：PocketBase 中实际为 datetime 类型
        },
        'focus_points': {
            'id': 'TEXT PRIMARY KEY',
            'focuspoint': 'TEXT NOT NULL',
            'restrictions': 'TEXT DEFAULT ""',
            'explanation': 'TEXT DEFAULT ""',
            'activated': 'BOOLEAN DEFAULT 1',
            'freq': 'NUMERIC DEFAULT 24',
            'search': 'BOOLEAN DEFAULT 0',
            'sources': 'JSON DEFAULT "[]"',
        },
        'sources': {
            'id': 'TEXT PRIMARY KEY',
            'type': 'TEXT CHECK(type IN ("web", "rss", "ks", "wb", "mp"))',
            'creators': 'TEXT DEFAULT ""',
            'url': 'TEXT'
        },
        'wb_cache': {
            'id': 'TEXT PRIMARY KEY',  # 对应字典中的 note_id
            'content': 'TEXT DEFAULT ""',
            'create_time': 'TEXT DEFAULT ""',
            'liked_count': 'TEXT DEFAULT ""',
            'comments_count': 'TEXT DEFAULT ""',
            'shared_count': 'TEXT DEFAULT ""',
            'note_url': 'TEXT DEFAULT ""',
            'ip_location': 'TEXT DEFAULT ""',
            'user_id': 'TEXT DEFAULT ""',
            'nickname': 'TEXT DEFAULT ""',
            'gender': 'TEXT DEFAULT ""',
            'profile_url': 'TEXT DEFAULT ""',
            'source_keyword': 'TEXT DEFAULT ""',
            'updated': 'TEXT'  # 注意：PocketBase 中实际为 datetime 类型
        },
        'ks_cache': {
            'id': 'TEXT PRIMARY KEY',  # 对应字典中的 video_id
            'video_type': 'TEXT DEFAULT ""',
            'title': 'TEXT DEFAULT ""',
            'desc': 'TEXT DEFAULT ""',
            'create_time': 'TEXT DEFAULT ""',
            'user_id': 'TEXT DEFAULT ""',
            'nickname': 'TEXT DEFAULT ""',
            'liked_count': 'TEXT DEFAULT ""',
            'viewd_count': 'TEXT DEFAULT ""',
            'video_url': 'TEXT DEFAULT ""',
            'video_play_url': 'TEXT DEFAULT ""',
            'source_keyword': 'TEXT DEFAULT ""',
            'updated': 'TEXT'  # 注意：PocketBase 中实际为 datetime 类型
        }
    }
    
    def __init__(self, pool_size: int = 6, max_retries: int = 3):
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
        self.ready = False

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
        self.ready = True

    async def _init_db_schema(self):
        """初始化数据库模式，包含表结构校验和缺失列自动补充"""
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            # 检查所有必需的表是否存在
            for table_name, expected_columns in self.TABLE_SCHEMAS.items():
                # 检查表是否存在
                async with db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                    (table_name,)
                ) as cursor:
                    table_exists = await cursor.fetchone()
                
                if not table_exists:
                    raise ValueError(f"Required table '{table_name}' does not exist")
                
                # 获取当前表的列信息
                async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
                    current_columns_info = await cursor.fetchall()
                
                # 构建当前列的详细信息 {列名: (类型, 是否非空)}
                current_columns = {}
                for row in current_columns_info:
                    col_name = row[1]
                    col_type = row[2]
                    current_columns[col_name] = {
                        'type': col_type,
                        'not_null': bool(row[3])
                    }
                
                # 检查所有必需的列是否存在
                for col_name, col_def in expected_columns.items():
                    if col_name not in current_columns:
                        raise ValueError(f"Required column '{col_name}' missing in table '{table_name}'")
                    
                    # 检查列类型是否匹配
                    expected_type = col_def.split()[0].upper()  # 获取类型部分并转为大写
                    current_type = current_columns[col_name]['type'].upper()
                    
                    # 类型匹配检查（包括 BOOLEAN 类型）
                    if expected_type != current_type:
                        raise ValueError(f"Column '{col_name}' in table '{table_name}' has incorrect type. Expected {expected_type}, got {current_type}")
                    
                    # 检查 NOT NULL 约束
                    if 'NOT NULL' in col_def.upper() and not current_columns[col_name]['not_null']:
                        raise ValueError(f"Column '{col_name}' in table '{table_name}' should be NOT NULL")
            
            # 检查并设置 crawled_data 表中 url 字段的唯一约束
            await self._ensure_url_unique_constraint(db)
            
            # 添加索引提高查询性能
            indexes = [
                ("idx_crawled_data_url", "crawled_data", "url"),
                # ("idx_infos_created", "infos", "updated"),
            ]
            
            for index_name, table_name, column_name in indexes:
                try:
                    await db.execute(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON {table_name}({column_name})
                    """)
                except Exception as e:
                    wis_logger.warning(f"Failed to create index {index_name}: {str(e)}")
            
            await db.commit()
            wis_logger.debug("Database schema validation completed")

    async def _ensure_url_unique_constraint(self, db):
        """确保 crawled_data 表中的 url 字段具有唯一约束"""
        try:
            # 检查是否已存在 url 字段的唯一索引
            async with db.execute("PRAGMA index_list('crawled_data')") as cursor:
                indexes = await cursor.fetchall()
            
            # 检查每个索引是否为 url 字段的唯一索引
            url_unique_exists = False
            for index_info in indexes:
                index_name = index_info[1]  # 索引名称
                is_unique = bool(index_info[2])  # 是否为唯一索引
                
                if is_unique:
                    # 检查索引的列信息
                    async with db.execute(f"PRAGMA index_info('{index_name}')") as cursor:
                        index_columns = await cursor.fetchall()
                    
                    # 检查是否只包含 url 字段
                    if (len(index_columns) == 1 and 
                        index_columns[0][2] == 'url'):  # 第三个元素是列名
                        url_unique_exists = True
                        wis_logger.debug(f"Found existing unique constraint on url field: {index_name}")
                        break
            
            # 如果不存在唯一约束，创建一个
            if not url_unique_exists:
                wis_logger.info("Url in crawled_data table is not unique, creating unique constraint")
                try:
                    await db.execute("""
                        CREATE UNIQUE INDEX idx_crawled_data_url_unique 
                        ON crawled_data(url)
                    """)
                    wis_logger.info("Successfully created unique constraint on crawled_data.url field")
                except Exception as e:
                    # 如果创建失败（可能因为已存在重复数据），记录错误但不中断初始化
                    wis_logger.error(f"Failed to create unique constraint on url field: {str(e)}")
                    wis_logger.error("This may be due to existing duplicate URLs in the database")
                    # 可以选择清理重复数据或提示用户手动处理
                    await self._handle_duplicate_urls(db)
            else:
                wis_logger.debug("URL field unique constraint already exists")
                
        except Exception as e:
            wis_logger.error(f"Error checking/setting url unique constraint: {str(e)}")

    async def _handle_duplicate_urls(self, db):
        """处理数据库中的重复URL"""
        try:
            # 查找重复的URL
            async with db.execute("""
                SELECT url, COUNT(*) as count 
                FROM crawled_data 
                GROUP BY url 
                HAVING COUNT(*) > 1
            """) as cursor:
                duplicates = await cursor.fetchall()
            
            if duplicates:
                wis_logger.warning(f"Found {len(duplicates)} duplicate URLs in database")
                
                # 对于每个重复的URL，保留最新的记录，删除其他的
                for url, count in duplicates:
                    wis_logger.debug(f"Cleaning duplicate URL: {url} (found {count} copies)")
                    
                    # 保留最新的记录（按updated字段排序）
                    await db.execute("""
                        DELETE FROM crawled_data 
                        WHERE url = ? AND id NOT IN (
                            SELECT id FROM crawled_data 
                            WHERE url = ? 
                            ORDER BY updated DESC 
                            LIMIT 1
                        )
                    """, (url, url))
                
                wis_logger.info(f"Cleaned up duplicate URLs, now attempting to create unique constraint")
                
                # 再次尝试创建唯一约束
                try:
                    await db.execute("""
                        CREATE UNIQUE INDEX idx_crawled_data_url_unique 
                        ON crawled_data(url)
                    """)
                    wis_logger.info("Successfully created unique constraint on crawled_data.url field after cleanup")
                except Exception as e:
                    wis_logger.error(f"Still failed to create unique constraint after cleanup: {str(e)}")
            else:
                wis_logger.debug("No duplicate URLs found, unique constraint creation failed for other reasons")
                
        except Exception as e:
            wis_logger.error(f"Error handling duplicate URLs: {str(e)}")

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
                    raise
                await asyncio.sleep(0.5 * (2 ** attempt))  # 指数退避

    def _generate_id(self) -> str:
        """
        生成符合要求的15位字符串id
        格式：只包含小写字母和数字 (a-z0-9)
        """
        return uuid.uuid4().hex[:15]

    def _get_utc_timestamp(self) -> str:
        """
        生成当前UTC时间的字符串，使用 ISO 8601 格式
        PocketBase datetime 字段兼容格式：YYYY-MM-DDTHH:MM:SS.sssZ
        """
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    async def cache_url(self, result: CrawlResult):
        """缓存URL数据 - 优化版本"""
        # 如果有重定向URL，使用重定向URL作为主键
        cache_url = result.redirected_url if result.redirected_url else result.url
        if not cache_url:
            return
        
        # 生成15位字符串id
        record_id = self._generate_id()
        
        # 获取当前UTC时间戳
        current_time = self._get_utc_timestamp()
        
        # 并发存储内容到文件系统
        content_tasks = []
        for field_name, mapping in self._content_field_map.items():
            if hasattr(result, field_name):
                content = getattr(result, field_name)
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
            # 不再处理 downloaded_files 字段
            
            await db.execute("""
                INSERT INTO crawled_data (
                    id, url, html, markdown,
                    link_dict, cleaned_html, screenshot,
                    title, author, publish_date, updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    html = excluded.html,
                    markdown = excluded.markdown,
                    link_dict = excluded.link_dict,
                    cleaned_html = excluded.cleaned_html,
                    screenshot = excluded.screenshot,
                    title = excluded.title,
                    author = excluded.author,
                    publish_date = excluded.publish_date,
                    updated = excluded.updated
            """, (
                record_id,
                cache_url,
                content_hashes.get("html", ""),
                content_hashes.get("markdown", ""),
                content_hashes.get("link_dict", ""),
                content_hashes.get("cleaned_html", ""),
                content_hashes.get("screenshot", ""),
                result.title or "",
                result.author or "",
                result.publish_date or "",
                current_time
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
                    updated_index = columns.index('updated')
                    updated_str = row[updated_index]
                    if self.is_cache_expired(updated_str, days_threshold):
                        wis_logger.debug(f"Cache for {url} expired (>{days_threshold} days). Returning None.")
                        return None
                except ValueError:
                    # 'updated' column not found, treat as not expired (or log a warning)
                    # This case should ideally not happen with schema initialization, but as a fallback
                    wis_logger.warning("Column 'updated' not found in crawled_data table. Cannot check cache expiration.")
                    return None
                except Exception as e:
                    # Handle potential errors during date parsing or comparison
                    wis_logger.error(f"Error checking cache expiration for {url}: {str(e)}")
                    return None

                row_dict = dict(zip(columns, row))
                
                # 并发加载内容从文件系统
                load_tasks = []
                for field_name, mapping in self._content_field_map.items():
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

                # 不再处理 downloaded_files 字段，设置为空列表以符合 CrawlResult 的要求
                row_dict["downloaded_files"] = []
                
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
            updated_at: 更新时间字符串，支持多种格式：
                       - ISO 8601: 'YYYY-MM-DDTHH:MM:SS.sssZ'
                       - 旧格式: 'YYYY-MM-DD HH:MM:SS UTC'
            days_threshold: 过期天数阈值，默认30天
            
        Returns:
            bool: True表示已过期，False表示未过期
        """
        if not updated_at:
            return True
            
        try:
            cache_time = None
            # 尝试解析 ISO 8601 格式 (新格式)
            if 'T' in updated_at and updated_at.endswith('Z'):
                # ISO 8601 格式: 2024-01-01T12:34:56.789Z
                iso_str = updated_at.rstrip('Z')
                cache_time = datetime.fromisoformat(iso_str)
            elif ' UTC' in updated_at:
                # 旧格式: 2024-01-01 12:34:56 UTC
                time_str = updated_at.replace(' UTC', '').strip()
                cache_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            else:
                # 尝试直接解析 ISO 格式（没有 Z 后缀）
                cache_time = datetime.fromisoformat(updated_at.replace('Z', ''))
            
            if cache_time is None:
                return True
                
            # 确保 cache_time 是 naive datetime (无时区信息)
            if cache_time.tzinfo is not None:
                cache_time = cache_time.replace(tzinfo=None)
                
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)
            
            # 计算时间差
            time_diff = current_time - cache_time
            
            # 检查是否超过阈值
            return time_diff > timedelta(days=days_threshold)
            
        except (ValueError, TypeError) as e:
            # 如果时间格式解析失败，认为缓存已过期
            wis_logger.warning(f"Failed to parse timestamp '{updated_at}': {e}")
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
        """反序列化JSON数据，支持 PocketBase 的 NULL 值"""
        if data is None or not data:
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

    async def add_info(self, content: str, focuspoint_id: str, source: str, references: str):
        """
        向 infos 表添加一条记录

        Args:
            content: 内容文本
            focuspoint_id: 关联的 focus_points 表的 id
            source: 关联的 sources 表的 id
            references: 引用信息，文本格式
        """
        # 生成15位字符串id
        record_id = self._generate_id()
        
        # 获取当前UTC时间戳
        current_time = self._get_utc_timestamp()

        async def _add(db):
            await db.execute("""
                INSERT INTO infos (id, content, focuspoint, source, [references], updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (record_id, content, focuspoint_id, source, references or "", current_time))

        try:
            await self.execute_with_retry(_add)
            wis_logger.debug("Successfully added info")
        except Exception as e:
            wis_logger.error(f"Error adding info for focuspoint {focuspoint_id}: {str(e)}")

    async def get_activated_focus_points_with_sources(self) -> List[dict]:
        """
        获取所有激活的 focus_points 及其关联的 sources
        
        Returns:
            List[dict]: 包含 focus_point 和关联 sources 的字典列表
                每个字典包含:
                - focus_point: focus_point 的所有字段
                - sources: 关联的 sources 列表
        """
        result = []
        
        async def _get_focus_points_with_sources(db):
            # 首先获取所有激活的 focus_points
            focus_points_query = """
                SELECT id, focuspoint, restrictions, explanation, activated, freq, search, sources
                FROM focus_points 
                WHERE activated = 1
            """
            
            async with db.execute(focus_points_query) as cursor:
                focus_points_rows = await cursor.fetchall()
                focus_points_columns = [desc[0] for desc in cursor.description]
            
            # 为每个 focus_point 获取关联的 sources
            for fp_row in focus_points_rows:
                # 构建 focus_point 字典
                focus_point_dict = dict(zip(focus_points_columns, fp_row))
                
                # 解析 sources JSON 字段
                sources_ids = self._deserialize_json(focus_point_dict.get('sources', '[]'), default_as_list=True)
                
                # 获取关联的 sources 详细信息
                sources_list = []
                if sources_ids:
                    # 构建 IN 查询的占位符
                    placeholders = ','.join(['?' for _ in sources_ids])
                    sources_query = f"""
                        SELECT id, type, creators, url
                        FROM sources 
                        WHERE id IN ({placeholders})
                    """
                    
                    async with db.execute(sources_query, sources_ids) as sources_cursor:
                        sources_rows = await sources_cursor.fetchall()
                        sources_columns = [desc[0] for desc in sources_cursor.description]
                        
                        for source_row in sources_rows:
                            source_dict = dict(zip(sources_columns, source_row))
                            # creators 现在是 TEXT 类型，直接作为字符串处理
                            source_dict['creators'] = source_dict.get('creators', '') or ''
                            sources_list.append(source_dict)
                
                # 将 focus_point 和关联的 sources 组合
                result.append({
                    'focus_point': focus_point_dict,
                    'sources': sources_list
                })
        
        try:
            await self.execute_with_retry(_get_focus_points_with_sources)
            wis_logger.debug(f"Retrieved {len(result)} activated focus points with their sources")
        except Exception as e:
            wis_logger.error(f"Error retrieving activated focus points with sources: {str(e)}")
            # 在出错时返回空列表
        
        return result

    async def get_infos(self, focuspoint_id: Optional[str] = None, 
                       source: Optional[str] = None, 
                       daysthreshold: Optional[int] = None) -> List[dict]:
        """
        从 infos 表读取数据，支持可选的筛选条件
        
        Args:
            focuspoint_id: 关联的 focus_points 表的 id，可选
            source: 关联的 sources 表的 id，可选
            daysthreshold: 时间阈值（天），仅返回指定天数内的记录，可选
            
        Returns:
            List[dict]: 符合条件的 infos 记录列表，每条记录为字典格式
        """
        result = []
        
        async def _get_infos(db):
            # 构建查询条件
            where_conditions = []
            params = []
            
            if focuspoint_id is not None:
                where_conditions.append("focuspoint = ?")
                params.append(focuspoint_id)
            
            if source is not None:
                where_conditions.append("source = ?")
                params.append(source)
            
            if daysthreshold is not None:
                # 计算时间阈值，使用UTC时间与数据库时间戳匹配
                threshold_time = datetime.now(timezone.utc) - timedelta(days=daysthreshold)
                threshold_str = threshold_time.strftime('%Y-%m-%d %H:%M:%S')
                where_conditions.append("updated >= ?")
                params.append(threshold_str)
            
            # 构建完整的查询语句
            base_query = "SELECT id, content, focuspoint, source, [references], updated FROM infos"
            if where_conditions:
                query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
            else:
                query = base_query
            
            # 按更新时间倒序排列
            query += " ORDER BY updated DESC"
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    result.append(row_dict)
        
        try:
            await self.execute_with_retry(_get_infos)
            wis_logger.debug(f"Retrieved {len(result)} info records with filters: "
                           f"focuspoint_id={focuspoint_id}, source={source}, "
                           f"daysthreshold={daysthreshold}")
        except Exception as e:
            wis_logger.error(f"Error retrieving infos: {str(e)}")
            # 在出错时返回空列表
        
        return result

    async def add_wb_cache(self, wb_data: dict):
        """
        向 wb_cache 表添加一条微博记录
        
        Args:
            wb_data: 微博数据字典，包含以下键值：
                - note_id: 微博ID（会被映射为数据库中的id字段）
                - content: 微博内容
                - create_time: 创建时间
                - liked_count: 点赞数
                - comments_count: 评论数
                - shared_count: 转发数
                - note_url: 微博链接
                - ip_location: IP位置
                - user_id: 用户ID
                - nickname: 用户昵称
                - gender: 性别
                - profile_url: 用户主页链接
                - source_keyword: 来源关键词
        """
        if not wb_data.get('note_id'):
            wis_logger.error("wb_data must contain 'note_id' field")
            return

        # 获取当前UTC时间戳
        current_time = self._get_utc_timestamp()

        async def _add_wb(db):
            await db.execute("""
                INSERT INTO wb_cache (
                    id, content, create_time, liked_count, comments_count, 
                    shared_count, note_url, ip_location, user_id, nickname, 
                    gender, profile_url, source_keyword, updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    content = excluded.content,
                    create_time = excluded.create_time,
                    liked_count = excluded.liked_count,
                    comments_count = excluded.comments_count,
                    shared_count = excluded.shared_count,
                    note_url = excluded.note_url,
                    ip_location = excluded.ip_location,
                    user_id = excluded.user_id,
                    nickname = excluded.nickname,
                    gender = excluded.gender,
                    profile_url = excluded.profile_url,
                    source_keyword = excluded.source_keyword,
                    updated = excluded.updated
            """, (
                wb_data.get('note_id', ''),
                wb_data.get('content', ''),
                wb_data.get('create_time', ''),
                wb_data.get('liked_count', ''),
                wb_data.get('comments_count', ''),
                wb_data.get('shared_count', ''),
                wb_data.get('note_url', ''),
                wb_data.get('ip_location', ''),
                wb_data.get('user_id', ''),
                wb_data.get('nickname', ''),
                wb_data.get('gender', ''),
                wb_data.get('profile_url', ''),
                wb_data.get('source_keyword', ''),
                current_time
            ))

        try:
            await self.execute_with_retry(_add_wb)
            wis_logger.debug(f"Successfully added/updated wb_cache for note_id: {wb_data.get('note_id')}")
        except Exception as e:
            wis_logger.error(f"Error adding wb_cache for note_id {wb_data.get('note_id')}: {str(e)}")

    async def get_wb_cache(self, 
                          note_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          source_keyword: Optional[str] = None,
                          daysthreshold: Optional[int] = None) -> List[dict]:
        """
        从 wb_cache 表读取微博数据，支持可选的筛选条件
        
        Args:
            note_id: 微博ID，可选
            user_id: 用户ID，可选
            source_keyword: 来源关键词，可选
            daysthreshold: 时间阈值（天），仅返回指定天数内的记录，可选
            
        Returns:
            List[dict]: 符合条件的微博记录列表，每条记录为字典格式
                注意：数据库中的 id 字段会被映射为字典中的 note_id 字段
        """
        result = []
        
        async def _get_wb_cache(db):
            # 构建查询条件
            where_conditions = []
            params = []
            
            if note_id is not None:
                where_conditions.append("id = ?")
                params.append(note_id)
            
            if user_id is not None:
                where_conditions.append("user_id = ?")
                params.append(user_id)
            
            if source_keyword is not None:
                where_conditions.append("source_keyword = ?")
                params.append(source_keyword)
            
            if daysthreshold is not None:
                # 计算时间阈值，使用UTC时间与数据库时间戳匹配
                threshold_time = datetime.now(timezone.utc) - timedelta(days=daysthreshold)
                threshold_str = threshold_time.strftime('%Y-%m-%d %H:%M:%S')
                where_conditions.append("updated >= ?")
                params.append(threshold_str)
            
            # 构建完整的查询语句
            base_query = """
                SELECT id, content, create_time, liked_count, comments_count, 
                       shared_count, note_url, ip_location, user_id, nickname, 
                       gender, profile_url, source_keyword, updated 
                FROM wb_cache
            """
            if where_conditions:
                query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
            else:
                query = base_query
            
            # 按更新时间倒序排列
            query += " ORDER BY updated DESC"
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    
                    # 将数据库中的 id 字段映射为字典中的 note_id 字段
                    if 'id' in row_dict:
                        row_dict['note_id'] = row_dict.pop('id')
                    
                    result.append(row_dict)
        
        try:
            await self.execute_with_retry(_get_wb_cache)
            wis_logger.debug(f"Retrieved {len(result)} wb_cache records with filters: "
                           f"note_id={note_id}, user_id={user_id}, "
                           f"source_keyword={source_keyword}, daysthreshold={daysthreshold}")
        except Exception as e:
            wis_logger.error(f"Error retrieving wb_cache: {str(e)}")
            # 在出错时返回空列表
        
        return result

    async def add_ks_cache(self, ks_data: dict):
        """
        向 ks_cache 表添加一条快手视频记录
        
        Args:
            ks_data: 快手视频数据字典，包含以下键值：
                - video_id: 视频ID（会被映射为数据库中的id字段）
                - video_type: 视频类型
                - title: 标题
                - desc: 描述
                - create_time: 创建时间
                - user_id: 用户ID
                - nickname: 用户昵称
                - liked_count: 点赞数
                - viewd_count: 观看数
                - video_url: 视频链接
                - video_play_url: 视频播放链接
                - source_keyword: 来源关键词
        """
        if not ks_data.get('video_id'):
            wis_logger.error("ks_data must contain 'video_id' field")
            return

        # 获取当前UTC时间戳
        current_time = self._get_utc_timestamp()

        async def _add_ks(db):
            await db.execute("""
                INSERT INTO ks_cache (
                    id, video_type, title, desc, create_time, user_id, 
                    nickname, liked_count, viewd_count, video_url, 
                    video_play_url, source_keyword, updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    video_type = excluded.video_type,
                    title = excluded.title,
                    desc = excluded.desc,
                    create_time = excluded.create_time,
                    user_id = excluded.user_id,
                    nickname = excluded.nickname,
                    liked_count = excluded.liked_count,
                    viewd_count = excluded.viewd_count,
                    video_url = excluded.video_url,
                    video_play_url = excluded.video_play_url,
                    source_keyword = excluded.source_keyword,
                    updated = excluded.updated
            """, (
                ks_data.get('video_id', ''),
                ks_data.get('video_type', ''),
                ks_data.get('title', ''),
                ks_data.get('desc', ''),
                ks_data.get('create_time', ''),
                ks_data.get('user_id', ''),
                ks_data.get('nickname', ''),
                ks_data.get('liked_count', ''),
                ks_data.get('viewd_count', ''),
                ks_data.get('video_url', ''),
                ks_data.get('video_play_url', ''),
                ks_data.get('source_keyword', ''),
                current_time
            ))

        try:
            await self.execute_with_retry(_add_ks)
            wis_logger.debug(f"Successfully added/updated ks_cache for video_id: {ks_data.get('video_id')}")
        except Exception as e:
            wis_logger.error(f"Error adding ks_cache for video_id {ks_data.get('video_id')}: {str(e)}")

    async def get_ks_cache(self, 
                          video_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          source_keyword: Optional[str] = None,
                          daysthreshold: Optional[int] = None) -> List[dict]:
        """
        从 ks_cache 表读取快手视频数据，支持可选的筛选条件
        
        Args:
            video_id: 视频ID，可选
            user_id: 用户ID，可选
            source_keyword: 来源关键词，可选
            daysthreshold: 时间阈值（天），仅返回指定天数内的记录，可选
            
        Returns:
            List[dict]: 符合条件的快手视频记录列表，每条记录为字典格式
                注意：数据库中的 id 字段会被映射为字典中的 video_id 字段
        """
        result = []
        
        async def _get_ks_cache(db):
            # 构建查询条件
            where_conditions = []
            params = []
            
            if video_id is not None:
                where_conditions.append("id = ?")
                params.append(video_id)
            
            if user_id is not None:
                where_conditions.append("user_id = ?")
                params.append(user_id)
            
            if source_keyword is not None:
                where_conditions.append("source_keyword = ?")
                params.append(source_keyword)
            
            if daysthreshold is not None:
                # 计算时间阈值，使用UTC时间与数据库时间戳匹配
                threshold_time = datetime.now(timezone.utc) - timedelta(days=daysthreshold)
                threshold_str = threshold_time.strftime('%Y-%m-%d %H:%M:%S')
                where_conditions.append("updated >= ?")
                params.append(threshold_str)
            
            # 构建完整的查询语句
            base_query = """
                SELECT id, video_type, title, desc, create_time, user_id, 
                       nickname, liked_count, viewd_count, video_url, 
                       video_play_url, source_keyword, updated 
                FROM ks_cache
            """
            if where_conditions:
                query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
            else:
                query = base_query
            
            # 按更新时间倒序排列
            query += " ORDER BY updated DESC"
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    
                    # 将数据库中的 id 字段映射为字典中的 video_id 字段
                    if 'id' in row_dict:
                        row_dict['video_id'] = row_dict.pop('id')
                    
                    result.append(row_dict)
        
        try:
            await self.execute_with_retry(_get_ks_cache)
            wis_logger.debug(f"Retrieved {len(result)} ks_cache records with filters: "
                           f"video_id={video_id}, user_id={user_id}, "
                           f"source_keyword={source_keyword}, daysthreshold={daysthreshold}")
        except Exception as e:
            wis_logger.error(f"Error retrieving ks_cache: {str(e)}")
            # 在出错时返回空列表
        
        return result
