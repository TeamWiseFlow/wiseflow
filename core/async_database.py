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
            'search': 'JSON DEFAULT "[]"',
            'sources': 'JSON DEFAULT "[]"',
            'role': 'TEXT DEFAULT ""',
            'purpose': 'TEXT DEFAULT ""',
            'custom_table': 'TEXT DEFAULT ""',
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
        
        # 不缓存的URL集合（从sources表中type为web的记录获取）
        self.no_cache_urls = set()
        
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
        # 加载不缓存的URL列表
        await self._load_no_cache_urls()
    
    async def _ensure_database_directory(self):
        """确保数据库目录存在"""
        if not os.path.exists(DB_PATH):
            wis_logger.info(f"Creating database directory: {DB_PATH}")
            os.makedirs(DB_PATH, exist_ok=True)

    def _generate_create_table_sql(self, table_name: str, columns: dict) -> str:
        """根据表结构定义生成CREATE TABLE SQL语句"""
        column_defs = []
        # SQL reserved keywords that need to be escaped
        reserved_keywords = {'references', 'order', 'group', 'having', 'where', 'select', 'from', 'join', 'table'}
        
        for col_name, col_def in columns.items():
            # Escape column names that are SQL reserved keywords
            if col_name.lower() in reserved_keywords:
                escaped_col_name = f"[{col_name}]"
            else:
                escaped_col_name = col_name
            column_defs.append(f"{escaped_col_name} {col_def}")
        
        columns_sql = ",\n    ".join(column_defs)
        return f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    {columns_sql}
)
        """.strip()

    async def _create_missing_table(self, db, table_name: str, expected_columns: dict):
        """创建缺失的表"""
        wis_logger.info(f"Creating missing table: {table_name}")
        create_sql = self._generate_create_table_sql(table_name, expected_columns)
        await db.execute(create_sql)
        wis_logger.info(f"Successfully created table: {table_name}")

    async def _init_db_schema(self):
        await self._ensure_database_directory()
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
                    # 创建缺失的表
                    await self._create_missing_table(db, table_name, expected_columns)
                    # 表创建后，重新获取列信息进行后续验证
                    async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
                        current_columns_info = await cursor.fetchall()
                else:
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
                
                reserved_keywords = {'references', 'order', 'group', 'having', 'where', 'select', 'from', 'join', 'table'}
                for col_name, col_def in expected_columns.items():
                    if col_name not in current_columns:
                        wis_logger.info(f"Adding missing column '{col_name}' to table '{table_name}'")
                        try:
                            # Escape column names that are SQL reserved keywords
                            if col_name.lower() in reserved_keywords:
                                escaped_col_name = f"[{col_name}]"
                            else:
                                escaped_col_name = col_name
                            await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {escaped_col_name} {col_def}")
                            wis_logger.info(f"Successfully added column '{col_name}' to table '{table_name}'")
                        except Exception as e:
                            wis_logger.warning(f"Failed to add column '{col_name}' to table '{table_name}': {str(e)}")
                        continue
                    
                    # 检查列类型是否匹配
                    expected_type = col_def.split()[0].upper()  # 获取类型部分并转为大写
                    current_type = current_columns[col_name]['type'].upper()
                    
                    # 特殊处理：允许focus_points表中search字段从BOOLEAN迁移到JSON
                    if (table_name == 'focus_points' and col_name == 'search' and
                        current_type == 'BOOLEAN' and expected_type == 'JSON'):
                        wis_logger.info(f"Allowing migration of focus_points.search from BOOLEAN to JSON")
                        continue
                    
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
                        # wis_logger.debug(f"Found existing unique constraint on url field: {index_name}")
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

    async def _load_no_cache_urls(self):
        """加载不缓存的URL列表（从sources表中type为web的记录获取）"""
        async def _load(db):
            urls = set()
            async with db.execute(
                "SELECT url FROM sources WHERE type = ? AND url IS NOT NULL AND url != ''", 
                ("web",)
            ) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    url = row[0].strip() if row[0] else None
                    if url:
                        urls.add(url)
            return urls
        
        self.no_cache_urls = await self.execute_with_retry(_load)

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
        cache_url = result.url
        if not cache_url:
            return
            
        # 检查是否在不缓存的URL列表中
        if cache_url in self.no_cache_urls:
            wis_logger.debug(f"Skipping cache for URL {cache_url} (found in web sources)")
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
                                    row_dict[field_name] = []
                            else:
                                row_dict[field_name] = None
                        else:
                            if mapping.is_json_content:
                                deserialized = self._deserialize_json(content)
                                if field_name == "link_dict" and not deserialized:
                                    row_dict[field_name] = {}
                                else:
                                    row_dict[field_name] = deserialized
                            else:
                                row_dict[field_name] = content
                
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
            wis_logger.info(f"Failed to load content from {file_path}: {e}, file maybe removed.")
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
                SELECT id, focuspoint, restrictions, explanation, activated, freq, search, sources, role, purpose, custom_table
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
                
                # 解析 search 字段（兼容从BOOLEAN到JSON的迁移）
                search_value = focus_point_dict.get('search', '[]')
                if isinstance(search_value, (int, bool)):
                    # 处理旧的BOOLEAN值迁移：
                    # 0/False -> 空数组（不搜索）
                    # 1/True -> 默认使用bing搜索
                    focus_point_dict['search'] = ['bing'] if search_value else []
                    wis_logger.debug(f"Migrated search field from boolean {search_value} to array {focus_point_dict['search']} for focus_point {focus_point_dict.get('id')}")
                else:
                    focus_point_dict['search'] = self._deserialize_json(search_value, default_as_list=True)
                
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
            # wis_logger.debug(f"Retrieved {len(result)} activated focus points with their sources")
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
            #wis_logger.debug(f"Successfully added/updated wb_cache for note_id: {wb_data.get('note_id')}")
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
            
            if note_id:
                where_conditions.append("id = ?")
                params.append(note_id)
            
            if user_id:
                where_conditions.append("user_id = ?")
                params.append(user_id)
            
            if source_keyword:
                where_conditions.append("source_keyword = ?")
                params.append(source_keyword)
            
            if daysthreshold:
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
            # wis_logger.debug(f"Successfully added/updated ks_cache for video_id: {ks_data.get('video_id')}")
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
            
            if video_id:
                where_conditions.append("id = ?")
                params.append(video_id)
            
            if user_id:
                where_conditions.append("user_id = ?")
                params.append(user_id)
            
            if source_keyword:
                where_conditions.append("source_keyword = ?")
                params.append(source_keyword)
            
            if daysthreshold:
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

    async def _get_table_schema_info(self, table_name: str) -> Optional[dict]:
        """
        获取表的结构信息（内部函数）
        
        Args:
            table_name: 表名称
            
        Returns:
            Optional[dict]: 包含表信息的字典，格式为:
                {
                    'exists': bool,  # 表是否存在
                    'columns': dict  # 字段名到类型的映射 {field_name: field_type}
                }
                如果获取失败则返回None
        """
        if not table_name:
            return None
            
        async def _get_schema_info(db):
            # 1. 检查表是否存在
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                (table_name,)
            ) as cursor:
                table_exists = await cursor.fetchone() is not None
            
            if not table_exists:
                return {'exists': False, 'columns': {}}
            
            # 2. 获取表的字段信息
            async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
                columns_info = await cursor.fetchall()
            
            if not columns_info:
                return {'exists': True, 'columns': {}}
            
            # 构建字段名到类型的映射
            columns = {col_info[1]: col_info[2].upper() for col_info in columns_info}
            
            return {'exists': True, 'columns': columns}
        
        try:
            return await self.execute_with_retry(_get_schema_info)
        except Exception as e:
            wis_logger.warning(f"Error retrieving schema info for table '{table_name}': {str(e)}")
            return None

    async def _add_missing_columns(self, table_name: str, columns: dict) -> dict:
        """
        检查并添加缺失的 focuspoint 和 source 字段
        
        Args:
            table_name: 表名称
            columns: 当前表的字段结构
            
        Returns:
            dict: 更新后的字段结构
        """
        updated_columns = columns.copy()
        missing_columns = []
        
        # 检查是否缺少 focuspoint 字段
        if 'focuspoint' not in columns:
            missing_columns.append('focuspoint')
            
        # 检查是否缺少 source 字段
        if 'source' not in columns:
            missing_columns.append('source')
        
        if missing_columns:
            async def _add_columns(db):
                for column_name in missing_columns:
                    try:
                        await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT")
                        updated_columns[column_name] = 'TEXT'
                        wis_logger.info(f"Added column '{column_name}' to table '{table_name}'")
                    except Exception as e:
                        wis_logger.warning(f"Failed to add column '{column_name}' to table '{table_name}': {str(e)}")
            
            try:
                await self.execute_with_retry(_add_columns)
            except Exception as e:
                wis_logger.warning(f"Error adding missing columns to table '{table_name}': {str(e)}")
        
        return updated_columns

    async def get_custom_table_schema(self, table_name: str) -> Optional[dict]:
        """
        获取自定义表的字段结构和第一行数据
        
        Args:
            table_name: 表名称
            
        Returns:
            Optional[dict]: 字段名到第一行值的映射字典，如果表不存在或读取失败则返回None
                           key是字段名称，value是该字段对应的第一行值，没有值则为空字符串
                           不包含 focuspoint、source、id、created、updated 字段
        """
        if not table_name:
            wis_logger.warning("Table name cannot be empty")
            return None
        
        # 使用共用的表结构信息获取函数
        schema_info = await self._get_table_schema_info(table_name)
        if not schema_info or not schema_info['exists']:
            wis_logger.warning(f"Table '{table_name}' does not exist")
            return None
        
        columns = schema_info['columns']
        if not columns:
            wis_logger.warning(f"Failed to get column information for table '{table_name}'")
            return None
        
        # 检查并添加缺失的 focuspoint 和 source 字段
        # pb 好像无效，先注释掉
        # columns = await self._add_missing_columns(table_name, columns)
        
        # 定义要排除的字段
        excluded_fields = {'focuspoint', 'source', 'id', 'created', 'updated'}
        
        # 获取第一行数据
        async def _get_first_row(db):
            first_row_values = {}
            try:
                async with db.execute(f"SELECT * FROM {table_name} LIMIT 1") as cursor:
                    first_row = await cursor.fetchone()
                    
                    if first_row:
                        # 将第一行的值与字段名对应
                        column_names = list(columns.keys())
                        for i, column_name in enumerate(column_names):
                            # 跳过排除的字段
                            if column_name in excluded_fields:
                                continue
                            # 将值转换为字符串，None值转为空字符串
                            value = first_row[i] if first_row[i] is not None else ''
                            first_row_values[column_name] = str(value)
                    else:
                        # 没有数据行，所有字段值设为空字符串（排除指定字段）
                        for column_name in columns.keys():
                            if column_name not in excluded_fields:
                                first_row_values[column_name] = ''
                            
            except Exception as e:
                wis_logger.warning(f"Failed to fetch first row from table '{table_name}': {str(e)}")
                # 即使获取第一行失败，也返回字段结构，值设为空字符串（排除指定字段）
                for column_name in columns.keys():
                    if column_name not in excluded_fields:
                        first_row_values[column_name] = ''
            
            return first_row_values
        
        try:
            result = await self.execute_with_retry(_get_first_row)
            if result:
                wis_logger.debug(f"Successfully retrieved schema for table '{table_name}' with {len(result)} columns (excluding {excluded_fields})")
            return result
        except Exception as e:
            wis_logger.warning(f"Error retrieving schema for table '{table_name}': {str(e)}")
            return None

    async def add_custom_info(self, custom_table: str, focuspoint_id: str, source: str, info: dict):
        """
        向自定义表添加信息记录
        
        Args:
            custom_table: 自定义表名
            focuspoint_id: 焦点ID
            source: 源ID  
            info: 要插入的信息字典
        """
        if not custom_table:
            wis_logger.error("Custom table name cannot be empty")
            return
            
        if not info:
            wis_logger.warning(f"Info dict is empty for custom table '{custom_table}'")
            return

        # 1. 使用共用函数获取表结构信息
        schema_info = await self._get_table_schema_info(custom_table)
        if not schema_info:
            wis_logger.error(f"Error getting schema info for table '{custom_table}'")
            return
            
        if not schema_info['exists']:
            wis_logger.error(f"Custom table '{custom_table}' does not exist in database")
            return
            
        table_columns = schema_info['columns']
        if not table_columns:
            wis_logger.error(f"Failed to get column information for table '{custom_table}'")
            return

        # 2. 检查字段差异并记录警告
        table_fields = set(table_columns.keys())
        info_fields = set(info.keys())
        
        missing_in_table = info_fields - table_fields
        if missing_in_table:
            wis_logger.warning(f"Table '{custom_table}' missing fields from info: {missing_in_table}")
        
        missing_in_info = table_fields - info_fields - {'focuspoint', 'source', 'updated', 'id', 'created'}
        if missing_in_info:
            wis_logger.warning(f"Info missing fields present in table '{custom_table}': {missing_in_info}")

        # 3. 准备数据进行插入
        insert_data = {}
        current_time = self._get_utc_timestamp()
        
        # 添加特殊字段
        if 'focuspoint' in table_columns:
            insert_data['focuspoint'] = focuspoint_id
        if 'source' in table_columns:
            insert_data['source'] = source
        if 'updated' in table_columns:
            insert_data['updated'] = current_time
        if 'created' in table_columns:
            insert_data['created'] = current_time

        insert_data['id'] = self._generate_id()

        # 处理info中的字段
        for field_name, field_value in info.items():
            if field_name not in table_columns:
                continue  # 跳过表中不存在的字段
                
            # 获取表中字段的类型
            field_type = table_columns[field_name]
            
            # 处理空值情况
            if field_value is None or field_value == '':
                insert_data[field_name] = ''
                continue
            
            # 尝试类型转换
            try:
                converted_value = self._convert_value_to_type(field_value, field_type)
                insert_data[field_name] = converted_value
            except Exception as e:
                wis_logger.warning(f"Failed to convert value '{field_value}' to type '{field_type}' for field '{field_name}' in table '{custom_table}': {str(e)}")
                # 转换失败则舍弃这个值
                continue

        # 为表中存在但info中没有的字段设置空值
        for field_name in table_columns:
            if field_name not in insert_data:
                insert_data[field_name] = ''

        # 4. 执行插入操作
        async def _insert_custom_info(db):
            if not insert_data:
                wis_logger.warning(f"No valid data to insert into table '{custom_table}'")
                return
                
            fields = list(insert_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            field_names = ', '.join(fields)
            values = [insert_data[field] for field in fields]
            
            query = f"INSERT INTO {custom_table} ({field_names}) VALUES ({placeholders})"
            await db.execute(query, values)

        try:
            await self.execute_with_retry(_insert_custom_info)
            wis_logger.debug(f"Successfully added info to custom table '{custom_table}' for focuspoint '{focuspoint_id}'")
        except Exception as e:
            wis_logger.error(f"Error adding info to custom table '{custom_table}': {str(e)}")

    def _convert_value_to_type(self, value: any, sql_type: str) -> any:
        """
        将值转换为指定的SQL类型
        
        Args:
            value: 要转换的值
            sql_type: SQL类型（如 TEXT, INTEGER, REAL, BOOLEAN等）
            
        Returns:
            转换后的值
            
        Raises:
            ValueError: 转换失败时抛出异常
        """
        if value is None:
            return ''
            
        sql_type = sql_type.upper()
        
        try:
            if sql_type in ['TEXT', 'VARCHAR', 'CHAR']:
                return str(value)
            elif sql_type in ['INTEGER', 'INT']:
                if isinstance(value, str) and value.strip() == '':
                    return 0
                return int(float(value))  # 先转float再转int，处理"3.0"这样的字符串
            elif sql_type in ['REAL', 'FLOAT', 'DOUBLE']:
                if isinstance(value, str) and value.strip() == '':
                    return 0.0
                return float(value)
            elif sql_type in ['BOOLEAN', 'BOOL']:
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ['true', '1', 'yes', 'on']:
                        return True
                    elif value_lower in ['false', '0', 'no', 'off', '']:
                        return False
                    else:
                        raise ValueError(f"Cannot convert '{value}' to boolean")
                elif isinstance(value, (int, float)):
                    return bool(value)
                else:
                    return bool(value)
            elif sql_type == 'JSON':
                if isinstance(value, (dict, list)):
                    return json.dumps(value, ensure_ascii=False)
                elif isinstance(value, str):
                    # 验证是否为有效JSON
                    json.loads(value)
                    return value
                else:
                    return json.dumps(value, ensure_ascii=False)
            else:
                # 对于未知类型，尝试转换为字符串
                return str(value)
                
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot convert value '{value}' to type '{sql_type}': {str(e)}")