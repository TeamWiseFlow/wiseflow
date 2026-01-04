import aiosqlite
import asyncio
import sqlite3
import uuid
from typing import Optional, List, Any, Dict
from contextlib import asynccontextmanager
import time
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import sys


def _detect_install_root() -> Path:
    # 1) Prefer explicit env from launchers for portable installs
    env_dir = os.getenv("WISEFLOW_BASE_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
        try:
            p.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        return p

    # 2) Use parent's parent of the current script
    return Path(__file__).resolve().parent.parent

    # 3) Fallback to user home
    return Path.home()

# Base directory for application data (portable if env/exe available)
base_directory = _detect_install_root()  / "work_dir"
base_directory.mkdir(parents=True, exist_ok=True)


class NonRetryableDatabaseError(Exception):
    """Raised to explicitly indicate an operation should not be retried."""
    pass


class AsyncDatabaseManager:
    # 表结构定义
    TABLE_SCHEMAS = {
        'infos': {
            'id': 'TEXT PRIMARY KEY DEFAULT (LOWER(HEX(RANDOMBLOB(8))))',
            'type': 'TEXT NOT NULL',
            'content': 'TEXT NOT NULL',
            'refers': 'TEXT DEFAULT ""',
            # 拼接 focuspoint（restrictions） - role/purpose 形成一个字符串，避免 focuspoint 更新的影响。info 因为反应的是当时的 focus point 信息，所以需要保留。
            'focus_statement': 'TEXT',
            'focus_id': 'INTEGER',
            'source_url': 'TEXT',
            'source_title': 'TEXT',
            'created': 'TEXT'
        },
        'tasks': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            # 这里直接引入 task 的focus组的概念, focuses 对应一个组，这个组里面包含多个 focuspoint，也可能不包含
            # 因为实践中有用户 focus 为 "微信 hook、微信逆向、视频号下载"，虽然都是同一套信源，但写成一个 focus 提取效果很差，需要分成三个 focus，分别提取
            # focuses 现在存储的是 focus 表的 id 列表，而不是完整的 focus 对象，通过关联查询获取完整信息
            'focuses': 'JSON DEFAULT "[]"',
            'search': 'JSON DEFAULT "[]"', # 只能从如下多选：bing、github、arxiv、ks, wb, bili, dy, zhihu， xhs
            # sources 对应一个列表，每个元素是一个 dict，含两个字段：type 和 detail
            # type 是 TEXT，只能从如下单选："web", "rss", "ks", "wb", "mp", "bili", "dy", "zhihu", "xhs"
            'sources': 'JSON DEFAULT "[]"',
            # 任务控制选项
            'activated': 'BOOLEAN DEFAULT 1',
            # 对应工作时间，是一个列表，只能从如下多选：first, second, third, fourth
            'time_slots': 'JSON DEFAULT "[]"',
            # 任务标题
            'title': 'TEXT DEFAULT ""',
            # status，对应状态，int。0：正常，2：存在无法进行的错误， 系统会跳过，除非状态码改变，1：存在需要提醒用户解决的错误，但系统会执行
            'status': 'NUMERIC DEFAULT 0',
            # 错误信息，TEXT，int0 时为空
            'errors': 'TEXT DEFAULT ""',
            'updated': 'TEXT'
        },
        'local_proxies': {
            # Int, 自增
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'ip': 'TEXT',
            'port': 'NUMERIC',
            'user': 'TEXT',
            'password': 'TEXT',
            'apply_to': 'JSON DEFAULT "[]"',
            'life_time': 'NUMERIC', # in minutes, 0 means never expire
            'updated': 'TEXT'
        },
        'kdl_proxies': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'SECERT_ID': 'TEXT',
            'SIGNATURE': 'TEXT',
            'USER_NAME': 'TEXT',
            'USER_PWD': 'TEXT',
            'apply_to': 'JSON DEFAULT "[]"',
            'updated': 'TEXT'
        },
        'mc_backup_accounts': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'platform_name': 'TEXT',
            'account_name': 'TEXT',
            'cookies': 'TEXT',
            'updated': 'TEXT'
        },
        'focuses': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'focuspoint': 'TEXT', # 不能为空
            'custom_schema': 'TEXT DEFAULT ""',
            'restrictions': 'TEXT DEFAULT ""',
            'explanation': 'TEXT DEFAULT ""',
            'role': 'TEXT DEFAULT ""',
            'purpose': 'TEXT DEFAULT ""',
            'created': 'TEXT'
        },
        'ws_history': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'type': 'TEXT',              # notify | prompt | prompt_resolved
            'prompt_id': 'TEXT',         # for prompt and prompt_resolved
            'code': 'NUMERIC',
            'params': 'JSON DEFAULT "[]"',
            'actions': 'JSON DEFAULT "[]"',  # for prompt
            'action_id': 'TEXT',         # for prompt_resolved
            'timeout': 'NUMERIC',        # seconds
            'ts': 'NUMERIC'              # unix timestamp seconds
        },
    }
    
    # 任务相关字段的允许值
    ALLOWED_SEARCH = {"bing", "github", "arxiv", "ks", "wb", "bili", "dy", "zhihu", "xhs"}
    ALLOWED_SOURCE_TYPES = {"web", "rss", "ks", "wb", "mp", "bili", "dy", "zhihu", "xhs"}
    ALLOWED_TIME_SLOTS = {'first', 'second', 'third', 'fourth'}
    
    def __init__(self, pool_size: int = 6, max_retries: int = 3, logger = None):
        self.db_path = base_directory / "data.db"
        self.max_retries = max_retries
        
        # 真正的连接池
        self._connection_pool: List[aiosqlite.Connection] = []
        self._pool_size = pool_size
        self._available_connections = asyncio.Queue(maxsize=pool_size)
        self._pool_initialized = False
        self._init_lock = asyncio.Lock()
        
        self.ready = False
        self.logger = logger

    async def initialize(self):
        """初始化数据库和连接池"""
        async with self._init_lock:
            if self._pool_initialized:
                return
                
            # self.logger.debug("Initializing optimized database manager")
            # 确保数据库表存在
            await self._init_db_schema()
            # 初始化真正的连接池
            await self._init_connection_pool()
            
            self._pool_initialized = True
            # self.logger.debug("Database manager initialized successfully")
            
        self.ready = True

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
        self.logger.info(f"Creating missing table: {table_name}")
        create_sql = self._generate_create_table_sql(table_name, expected_columns)
        await db.execute(create_sql)
        self.logger.info(f"Successfully created table: {table_name}")

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
                        # 添加缺失的列
                        self.logger.info(f"Adding missing column '{col_name}' to table '{table_name}'")
                        try:
                            # Escape column names that are SQL reserved keywords
                            if col_name.lower() in reserved_keywords:
                                escaped_col_name = f"[{col_name}]"
                            else:
                                escaped_col_name = col_name
                            await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {escaped_col_name} {col_def}")
                            self.logger.info(f"Successfully added column '{col_name}' to table '{table_name}'")
                        except Exception as e:
                            self.logger.warning(f"Failed to add column '{col_name}' to table '{table_name}': {str(e)}")
                        continue
                    
                    # 检查列类型是否匹配
                    expected_type = col_def.split()[0].upper()  # 获取类型部分并转为大写
                    current_type = current_columns[col_name]['type'].upper()
                    
                    # 类型匹配检查（包括 BOOLEAN 类型）
                    if expected_type != current_type:
                        raise ValueError(f"Column '{col_name}' in table '{table_name}' has incorrect type. Expected {expected_type}, got {current_type}")
                    
                    # 检查 NOT NULL 约束
                    if 'NOT NULL' in col_def.upper() and not current_columns[col_name]['not_null']:
                        raise ValueError(f"Column '{col_name}' in table '{table_name}' should be NOT NULL")
            
            # 创建索引
            await self._create_indexes(db)
            
            await db.commit()
            # self.logger.debug("Database schema validation completed")

    async def _create_indexes(self, db):
        """创建数据库索引"""
        # 定义需要创建的索引
        # 注意：暂不为 focuses 表创建唯一索引，因为现有数据可能存在重复
        # 如果将来需要添加唯一约束，需要先清理重复数据，然后添加：
        # 'idx_focuses_unique': '''CREATE UNIQUE INDEX IF NOT EXISTS idx_focuses_unique 
        #                          ON focuses (focuspoint, restrictions, explanation, role, purpose, custom_schema)'''
        indexes = {
            'idx_infos_created_at': 'CREATE INDEX IF NOT EXISTS idx_infos_created_at ON infos (created)',
            'idx_ws_history_ts': 'CREATE INDEX IF NOT EXISTS idx_ws_history_ts ON ws_history (ts)'
        }
        
        for index_name, create_sql in indexes.items():
            try:
                await db.execute(create_sql)
                # self.logger.debug(f"Successfully created or verified index: {index_name}")
            except Exception as e:
                self.logger.warning(f"Failed to create index {index_name}: {str(e)}")

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

    def _is_retryable_error(self, error: Exception) -> bool:
        """判断异常是否值得重试。

        仅对明显的暂时性错误进行重试，比如 SQLite 的锁冲突等。
        对于对象不存在、约束冲突、语法错误、只读库等，直接视为不可重试。
        """
        # 调用方显式声明不可重试
        if isinstance(error, NonRetryableDatabaseError):
            return False

        # 明确不可重试的异常类型
        non_retryable_types = (
            aiosqlite.IntegrityError,
            aiosqlite.ProgrammingError,
            sqlite3.IntegrityError,
            sqlite3.ProgrammingError,
            ValueError,
            KeyError,
            TypeError,
        )
        if isinstance(error, non_retryable_types):
            return False

        message = str(error).lower()

        # 明确不可重试的错误信息
        non_retryable_keywords = (
            "no such table",
            "no such column",
            "unique constraint failed",
            "not null constraint failed",
            "foreign key constraint failed",
            "readonly database",
            "file is encrypted or is not a database",
            "malformed",
            "syntax error",
            "unable to open database file",
        )
        if any(k in message for k in non_retryable_keywords):
            return False

        return True

    async def execute_with_retry(self, operation, *args):
        """带重试的数据库操作执行，智能判断是否需要重试"""
        for attempt in range(self.max_retries):
            try:
                async with self.get_connection() as db:
                    result = await operation(db, *args)
                    await db.commit()
                    return result
            except Exception as e:
                # 非重试性错误，直接抛出
                if not self._is_retryable_error(e):
                    self.logger.warning(e)
                    raise

                # 如果是最后一次尝试，直接抛出异常
                if attempt == self.max_retries - 1:
                    self.logger.warning(f"Max retries ({self.max_retries}) exceeded for operation")
                    raise

                # 记录重试信息并指数退避
                wait_time = 0.5 * (2 ** attempt)
                await asyncio.sleep(wait_time)

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
            self.logger.warning(f"Failed to parse timestamp '{updated_at}': {e}")
            return True

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
            async with db.execute("SELECT COUNT(*) FROM infos") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

        try:
            return await self.execute_with_retry(_count)
        except Exception as e:
            self.logger.error(f"Error getting total count: {str(e)}")
            return 0

    async def cleanup(self):
        """清理资源"""
        # 关闭所有连接
        for conn in self._connection_pool:
            await conn.close()
        self._connection_pool.clear()

    async def add_info(
        self,
        type: str,
        content: str,
        refers: str,
        source_url: str,
        source_title: str,
        created: str,
        focus_statement: str,
        focus_id: int,
        id: Optional[str] = None
    ):
        """
        向 infos 表添加一条记录

        Args:
            type: 记录类型
            content: 内容文本
            refers: 引用信息，文本格式
            source_url: 关联的 sources 表的 url
            source_title: 关联的 sources 表的 title
            created: 创建时间字符串
            focus_statement: 记录信息时的 focuspoint 描述字符串
            focus_id: 关联的 focus 表的 id
            id: 记录的唯一标识符，可选。如果不提供，将由数据库自动生成
        """
        async def _add(db):
            if id:
                sql = """
                INSERT OR IGNORE INTO infos (id, type, content, focus_statement, focus_id, source_url, source_title, refers, created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """
                params = (
                    id,
                    type,
                    content,
                    focus_statement,
                    focus_id,
                    source_url,
                    source_title,
                    refers or "",
                    created,
                )
            else:
                sql = """
                INSERT OR IGNORE INTO infos (type, content, focus_statement, focus_id, source_url, source_title, refers, created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """
                params = (
                    type,
                    content,
                    focus_statement,
                    focus_id,
                    source_url,
                    source_title,
                    refers or "",
                    created,
                )
            
            async with db.execute(sql, params) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

        try:
            inserted_id = await self.execute_with_retry(_add)
            if inserted_id:
                self.logger.debug(f"Successfully added info with id: {inserted_id}")
                return inserted_id
            else:
                if id:
                    self.logger.info(f"Info with id {id} already exists, skipping insertion")
                    return id
                else:
                    self.logger.info("Info insertion skipped")
                    return None
        except Exception as e:
            self.logger.warning(f"Error adding info: {str(e)}\ncontext: {id}\n{type}\n{content}\n{refers}\n{source_url}\n{source_title}\n{created}\n{focus_statement}\n{focus_id}")
            return None

    async def filter_infos(self, id: Optional[str] = None,
                          source_url: Optional[str] = None,
                          # 新增的过滤与分页条件
                          focus_ids: Optional[List[int]] = None,
                          start_time: Optional[str] = None,
                          end_time: Optional[str] = None,
                          per_focus_limit: Optional[int] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> List[dict]:
        """
        从 infos 表读取数据，支持筛选条件：focus_ids、source_url、start_time、end_time、per_focus_limit、limit、offset
            
        Returns:
            List[dict]: 符合条件的 infos 记录列表，每条记录为字典格式
        """
        result = []
        
        async def _filter_infos(db):
            # 如果提供了 id，则忽略其他条件
            if id is not None:
                base_query = (
                    "SELECT id, type, content, focus_statement, focus_id, source_url, source_title, refers, created FROM infos"
                )
                query = f"{base_query} WHERE id = ?"
                params = [id]
            else:
                # 构建查询条件
                where_conditions = []
                params = []
                
                # 批量 focus 过滤
                if focus_ids:
                    placeholders = ','.join(['?'] * len(focus_ids))
                    where_conditions.append(f"focus_id IN ({placeholders})")
                    params.extend([int(x) for x in focus_ids])
                
                if source_url is not None:
                    where_conditions.append("source_url = ?")
                    params.append(source_url)

                # start_time / end_time 区间过滤（ISO8601 字符串，含 Z）
                if start_time:
                    try:
                        _ = datetime.fromisoformat(start_time.replace('Z', ''))
                        where_conditions.append("created >= ?")
                        params.append(start_time)
                    except Exception:
                        self.logger.warning(f"Invalid start_time: {start_time}")
                        pass
                if end_time:
                    try:
                        _ = datetime.fromisoformat(end_time.replace('Z', ''))
                        where_conditions.append("created <= ?")
                        params.append(end_time)
                    except Exception:
                        self.logger.warning(f"Invalid end_time: {end_time}")
                        pass
                
                # 列集合
                columns = "id, type, content, focus_statement, focus_id, source_url, source_title, refers, created"
                base_query = f"SELECT {columns} FROM infos"

                # 若需要按 focus_id 进行每组限制，优先尝试使用窗口函数
                if per_focus_limit is not None and per_focus_limit > 0 and focus_ids:
                    where_sql = f" WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
                    window_query = (
                        f"SELECT {columns} FROM ("
                        f"  SELECT {columns}, ROW_NUMBER() OVER (PARTITION BY focus_id ORDER BY created DESC) AS rn"
                        f"  FROM infos{where_sql}"
                        f") t WHERE rn <= ? ORDER BY created DESC"
                    )
                    try:
                        async with db.execute(window_query, params + [int(per_focus_limit)]) as cursor:
                            rows = await cursor.fetchall()
                            colnames = [desc[0] for desc in cursor.description]
                            for row in rows:
                                result.append(dict(zip(colnames, row)))
                        return  # early return via outer try; result consumed below
                    except Exception as e:
                        # 窗口函数不可用或其他失败，回退到应用层分组逻辑
                        pass

                # 常规路径：构建完整查询并可选分页
                if where_conditions:
                    query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
                else:
                    query = base_query

                # 排序与分页（按 created 倒序）
                query += " ORDER BY created DESC"

                # 若未指定每组限制，则可以使用总量 limit/offset 进行分页
                if not focus_ids and limit is not None:
                    if offset is None:
                        offset_val = 0
                    else:
                        offset_val = int(offset)
                    query += " LIMIT ? OFFSET ?"
                    exec_params = params + [int(limit), offset_val]
                else:
                    exec_params = params

                # 执行查询
                async with db.execute(query, exec_params) as cursor:
                    # 如果需要每组限制但没有窗口函数支持，则在应用层过滤
                    if per_focus_limit is not None and per_focus_limit > 0 and focus_ids:
                        per_focus_counts: dict[int, int] = {int(fid): 0 for fid in focus_ids}
                        colnames = [desc[0] for desc in cursor.description]
                        async for row in cursor:
                            row_dict = dict(zip(colnames, row))
                            fid = int(row_dict.get('focus_id')) if row_dict.get('focus_id') is not None else None
                            if fid is None or fid not in per_focus_counts:
                                continue
                            if per_focus_counts[fid] < int(per_focus_limit):
                                result.append(row_dict)
                                per_focus_counts[fid] += 1
                                # 若所有 focus 均已达到上限，则可提前结束
                                if all(c >= int(per_focus_limit) for c in per_focus_counts.values()):
                                    break
                    else:
                        rows = await cursor.fetchall()
                        colnames = [desc[0] for desc in cursor.description]
                        for row in rows:
                            result.append(dict(zip(colnames, row)))
        
        try:
            await self.execute_with_retry(_filter_infos)
        except Exception as e:
            self.logger.error(f"Error filtering infos: {str(e)}")
            return None
        
        return result

    async def delete_info(self, info_id: str) -> Optional[str]:
        """
        根据 id 删除指定的 info 记录
        
        Args:
            info_id: 要删除的 info 记录的 id
            
        """
        if not info_id:
            self.logger.warning("Info ID cannot be empty")
            return None

        async def _delete(db):
            await db.execute("DELETE FROM infos WHERE id = ?", (info_id,))

        try:
            await self.execute_with_retry(_delete)
            self.logger.debug(f"Successfully deleted info with id: {info_id}")
            return info_id
        except Exception as e:
            self.logger.error(f"Error deleting info {info_id}: {str(e)}")
            return None

    async def count_infos_by_focus(self, focus_id: Optional[int] = None) -> Dict[int, int]:
        """
        统计 infos 数量，按 focus_id 分组
        
        Args:
            focus_id: 可选的 focus_id，如果提供则只统计该 focus_id 的数量
            
        Returns:
            Dict[int, int]: 字典，key 为 focus_id，value 为该 focus_id 的 infos 数量
        """
        result = {}
        
        async def _count(db):
            if focus_id is not None:
                # 只统计指定的 focus_id
                async with db.execute(
                    "SELECT focus_id, COUNT(*) as count FROM infos WHERE focus_id = ? GROUP BY focus_id",
                    (focus_id,)
                ) as cursor:
                    async for row in cursor:
                        fid = row[0]
                        count = row[1]
                        if fid is not None:
                            result[int(fid)] = int(count)
            else:
                # 统计所有 focus_id
                async with db.execute(
                    "SELECT focus_id, COUNT(*) as count FROM infos GROUP BY focus_id"
                ) as cursor:
                    async for row in cursor:
                        fid = row[0]
                        count = row[1]
                        if fid is not None:
                            result[int(fid)] = int(count)
        
        try:
            await self.execute_with_retry(_count)
            return result
        except Exception as e:
            self.logger.error(f"Error counting infos by focus: {str(e)}")
            return {}
    
    # ---------------------- tasks CRUD ----------------------
    def _validate_task_inputs(self, search: list | None, sources: list | None, time_slots: list | None) -> str | None:
        """校验任务字段值是否合法，非法返回错误信息字符串，合法返回 None"""
        # search 校验
        if search is not None:
            if not isinstance(search, list) or any(not isinstance(s, str) for s in search):
                return "search 必须为字符串列表"
            for s in search:
                if s not in self.ALLOWED_SEARCH:
                    return f"search 包含非法值: {s}"

        # sources 校验
        if sources is not None:
            if not isinstance(sources, list):
                return "sources 必须为列表"
            for src in sources:
                if not isinstance(src, dict):
                    return "sources 列表元素必须为对象"
                src_type = src.get('type')
                if src_type not in self.ALLOWED_SOURCE_TYPES:
                    return f"sources.type 非法: {src_type}"
                if 'detail' not in src:
                    return "sources 每项必须包含 detail 字段"
                detail = src.get('detail')
                if not isinstance(detail, list):
                    return "sources.detail 必须为列表"
                if any(not isinstance(item, str) for item in detail):
                    return "sources.detail 列表元素必须为字符串"

        # time_slots 校验
        if time_slots is not None:
            if not isinstance(time_slots, list) or any(not isinstance(t, str) for t in time_slots):
                return "time_slots 必须为字符串列表"
            for t in time_slots:
                if t not in self.ALLOWED_TIME_SLOTS:
                    return f"time_slots 包含非法值: {t}"

        return None
    
    def _process_web_sources(self, sources: list) -> list:
        """
        处理 sources 列表：
        - 对于所有类型，合并相同 type 的 source，detail 列表去重
        - 对于 type 为 'web' 或 'rss' 的条目，先对 detail 列表中的每一项使用 extract_urls 拆分，然后将所有拆分出的 URL 合并
        
        Args:
            sources: 原始 sources 列表，每个 source 的 detail 字段为字符串列表
            
        Returns:
            处理后的 sources 列表，detail 字段始终为列表格式
        """
        if not sources:
            return sources or []
            
        from core.wis.utils import extract_urls
        
        # 用于合并相同 type 的 source
        merged_sources = {}
        
        for source in sources:
            if not isinstance(source, dict):
                continue
                
            source_type = source.get('type')
            detail = source.get('detail', [])

            if not source_type or not detail:
                continue
            
            # 确保 detail 是list[str]
            if isinstance(detail, list):
                pass
            elif isinstance(detail, str):
                detail = [detail]
            else:
                continue
            
            # 初始化合并的 source
            if source_type not in merged_sources:
                merged_sources[source_type] = {
                    'type': source_type,
                    'detail': []
                }
            
            if source_type in ['web', 'rss']:
                # 对于 web 和 rss 类型，先对 detail 列表中的每一项使用 extract_urls 拆分
                for d in detail:
                    if not isinstance(d, str) or not d.strip():
                        continue
                    # 使用 extract_urls 解析 URL
                    extracted_urls = extract_urls(d)
                    if extracted_urls:
                        # 将拆分出的 URL 添加到合并列表中并去重
                        for url in extracted_urls:
                            url_stripped = url.strip()
                            if url_stripped and url_stripped not in merged_sources[source_type]['detail']:
                                merged_sources[source_type]['detail'].append(url_stripped)
            else:
                # 对于其他类型，直接添加 detail 项并去重
                for item in detail:
                    if isinstance(item, str) and item.strip():
                        item_stripped = item.strip()
                        # if item_stripped not in ['?', '？'] and len(item_stripped) < 3:
                        #    continue
                        if item_stripped not in merged_sources[source_type]['detail']:
                            merged_sources[source_type]['detail'].append(item_stripped)
        
        # 返回合并后的 sources 列表
        return list(merged_sources.values())

    def _is_focus_payload_empty(self, focus: dict) -> bool:
        """
        判断 focus 是否需要被忽略：仅当 focuspoint/restrictions/role/purpose
        这四个字段全部为空字符串或缺失时视为“空 focus”
        """
        focus_fields = ('focuspoint', 'restrictions', 'role', 'purpose')
        for field in focus_fields:
            value = focus.get(field)
            if isinstance(value, str):
                if value.strip():
                    return False
            elif value not in (None, ''):
                return False

        return True

    async def add_task(self,
                       focuses: list = None,
                       search: list = None,
                       sources: list = None,
                       activated: bool = True,
                       time_slots: list = None,
                       title: str = "",
                       status: int = 0,
                       errors: set = None) -> Optional[int]:
        """  
        新增一条 task，返回生成的 id
        
        Args:
            focuses: focus 列表，每个元素可以是：
                    - dict: 包含 focuspoint, restrictions, explanation, role, purpose, custom_schema，会创建新的 focus 记录
                    - int: 现有的 focus id
        """
        # 字段校验（先于任何数据库写入）
        error_msg = self._validate_task_inputs(
            search=search or [],
            sources=sources or [],
            time_slots=time_slots or []
        )
        if error_msg:
            self.logger.warning(f"add_task 参数非法: {error_msg}")
            return None

        now = self._get_utc_timestamp()
        
        # 处理 focuses 参数：为 dict 类型的 focus 创建记录，获取 focus_ids
        focus_ids = set()
        if focuses:
            for focus_item in focuses:
                if isinstance(focus_item, dict):
                    if self._is_focus_payload_empty(focus_item):
                        continue
                    # 如果是 dict，创建新的 focus 记录
                    focus_id = await self.create_or_update_focus(
                        focuspoint=focus_item.get('focuspoint', ''),
                        restrictions=focus_item.get('restrictions', ''),
                        explanation=focus_item.get('explanation', ''),
                        role=focus_item.get('role', ''),
                        purpose=focus_item.get('purpose', ''),
                        custom_schema=focus_item.get('custom_schema', '')
                    )
                    if focus_id:
                        focus_ids.add(focus_id)
                elif isinstance(focus_item, int):
                    # 如果是 int，直接使用现有的 focus id
                    focus_ids.add(focus_item)
                else:
                    self.logger.warning(f"Invalid focus item type: {type(focus_item)}, expected dict or int")
        
        # 处理 sources: 对 type 为 'web' 的条目使用 extract_urls 处理
        processed_sources = self._process_web_sources(sources)
        
        # 处理 error_msg: 如果是 set 类型，用 "|" 拼接成字符串
        errors_str = ""
        if errors:
            errors_str = "|".join(str(item) for item in errors)
        
        async def _add(db):
            cursor = await db.execute(
                """
                INSERT INTO tasks (focuses, search, sources, activated, time_slots, title, status, errors, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self._serialize_json(list(focus_ids), default_as_list=True),  # 存储 focus_ids 而不是原始 focuses
                    self._serialize_json(search or [], default_as_list=True),
                    self._serialize_json(processed_sources, default_as_list=True),
                    1 if activated else 0,
                    self._serialize_json(time_slots or [], default_as_list=True),
                    (title or "").strip(),
                    status or 0,
                    errors_str,
                    now,
                ),
            )
            return cursor.lastrowid

        try:
            return await self.execute_with_retry(_add)
        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            return None

    async def list_tasks(self, only_activated: bool = False) -> List[dict]:
        result: List[dict] = []

        async def _list(db):
            base = "SELECT id, focuses, search, sources, activated, time_slots, title, status, errors, updated FROM tasks"
            query = base + (" WHERE activated = 1" if only_activated else "") + " ORDER BY id DESC"
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                for r in rows:
                    item = dict(zip(cols, r))
                    # 反序列化 JSON 字段
                    focus_ids = self._deserialize_json(item.get('focuses', '[]'), default_as_list=True)
                    item['search'] = self._deserialize_json(item.get('search', '[]'), default_as_list=True)
                    sources = self._deserialize_json(item.get('sources', '[]'), default_as_list=True)
                    item['time_slots'] = self._deserialize_json(item.get('time_slots', '[]'), default_as_list=True)
                    
                    # 规范化 sources：确保每个 source 的 detail 是列表格式（兼容旧数据）
                    normalized_sources = []
                    for src in sources:
                        if not isinstance(src, dict):
                            continue
                        normalized_src = src.copy()
                        detail = src.get('detail', [])
                        # 如果是字符串，转换为列表；如果已经是列表，保持不变
                        if isinstance(detail, str):
                            normalized_src['detail'] = [detail] if detail else []
                        elif not isinstance(detail, list):
                            normalized_src['detail'] = []
                        else:
                            normalized_src['detail'] = detail
                        normalized_sources.append(normalized_src)
                    item['sources'] = normalized_sources
                    
                    # 转换布尔值字段
                    item['activated'] = bool(item.get('activated', 1))
                    
                    # 处理 errors：用 '|' split 并转为 set
                    errors = item.get('errors', '') or ''
                    if errors:
                        item['errors'] = errors.split('|')
                    else:
                        item['errors'] = []
                    
                    # 关联读取 focus 信息
                    if focus_ids:      
                        item['focuses'] = await self.get_focuses_by_ids(focus_ids)
                    else:
                        item['focuses'] = []
                    
                    result.append(item)

        try:
            await self.execute_with_retry(_list)
        except Exception as e:
            self.logger.error(f"Error listing tasks: {e}")
            return None
        return result

    async def update_task(self, task_id: int, **fields) -> Optional[int]:
        """
        更新 task，自动刷新 updated。支持的字段：focuses, search, sources, activated, time_slots, status, errors
        
        Args:
            focuses: focus 列表，每个元素可以是：
                    - dict: 包含 focuspoint, restrictions, explanation, role, purpose, custom_schema，会创建新的 focus 记录
                    - int: 现有的 focus id
            errors: 错误信息集合，set 类型
        """
        if not task_id:
            return None
        allowed = {"focuses", "search", "sources", "activated", "time_slots", "title", "status", "errors", "updated"}
        updates = {}
        
        # 仅校验用户传入的字段
        validation_error = self._validate_task_inputs(
            search=fields.get('search', None),
            sources=fields.get('sources', None),
            time_slots=fields.get('time_slots', None)
        )
        if validation_error:
            self.logger.warning(f"update_task 参数非法: {validation_error}")
            return None

        # 检查是否传入了 error_msg，如果没有则清空错误并重置状态
        if 'errors' not in fields:
            updates['errors'] = ""
            updates['status'] = 0
        
        for k, v in fields.items():
            if k not in allowed:
                continue
                
            if k == "focuses":
                # 特殊处理 focuses 字段
                focus_ids = set()
                if v:
                    for focus_item in v:
                        if isinstance(focus_item, dict):
                            if self._is_focus_payload_empty(focus_item):
                                continue
                            # 如果是 dict，创建新的 focus 记录
                            focus_id = await self.create_or_update_focus(
                                focuspoint=focus_item.get('focuspoint', ''),
                                restrictions=focus_item.get('restrictions', ''),
                                explanation=focus_item.get('explanation', ''),
                                role=focus_item.get('role', ''),
                                purpose=focus_item.get('purpose', ''),
                                custom_schema=focus_item.get('custom_schema', '')
                            )
                            if focus_id:
                                focus_ids.add(focus_id)
                        elif isinstance(focus_item, int):
                            # 如果是 int，直接使用现有的 focus id
                            focus_ids.add(focus_item)
                        else:
                            self.logger.warning(f"Invalid focus item type: {type(focus_item)}, expected dict or int")
                updates[k] = self._serialize_json(list(focus_ids), default_as_list=True)
            elif k == "sources":
                # 特殊处理 sources 字段：对 type 为 'web' 的条目使用 extract_urls 处理
                processed_sources = self._process_web_sources(v)
                updates[k] = self._serialize_json(processed_sources, default_as_list=True)
            elif k in {"search", "time_slots"}:
                updates[k] = self._serialize_json(v or [], default_as_list=True)
            elif k == "activated":
                updates[k] = 1 if v else 0
            elif k == "errors":
                # 处理 error_msg: 如果是 set 类型，用 "|" 拼接成字符串
                if v:
                    updates['errors'] = "|".join(str(item) for item in v)
                else:
                    updates['errors'] = ""
                    updates['status'] = 0
            else:
                updates[k] = v

        # 如果传入了 errors 但没有传入 status，则不自动重置 status
        # 只有当完全没有传入 errors 时才会清空错误并重置状态（在开头已经处理）

        if not updates:
            return task_id

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        params = list(updates.values()) + [task_id]

        async def _upd(db):
            await db.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", params)

        try:
            await self.execute_with_retry(_upd)
            return task_id
        except Exception as e:
            self.logger.error(f"Error updating task {task_id}: {e}")
            return None

    async def delete_task(self, task_id: int) -> Optional[int]:
        if not task_id:
            return None

        async def _del(db):
            await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        try:
            await self.execute_with_retry(_del)
            return task_id
        except Exception as e:
            self.logger.error(f"Error deleting task {task_id}: {e}")
            return None

    async def clear_task_error(self, task_id: int) -> Optional[int]:
        """
        清除指定 task 的错误信息并将状态重置为正常
        
        Args:
            task_id: task 的 id
            
        Returns:
            bool: 操作是否成功
        """
        if not task_id:
            return None

        async def _clear_error(db):
            await db.execute(
                "UPDATE tasks SET errors = ?, status = ?, updated = ? WHERE id = ?",
                ("", 0, self._get_utc_timestamp(), task_id)
            )

        try:
            await self.execute_with_retry(_clear_error)
            self.logger.debug(f"Successfully cleared error for task {task_id}")
            return task_id
        except Exception as e:
            self.logger.error(f"Error clearing task error for {task_id}: {e}")
            return None

    # ---------------------- local_proxies CRUD ----------------------
    async def add_local_proxy(self, ip: str, port: int, user: str = '', password: str = '', life_time: int = 0, apply_to: Optional[List[str]] = None) -> Optional[int]:
        """新增一条本地代理记录，返回自增id"""
        now = self._get_utc_timestamp()
        async def _add(db):
            cursor = await db.execute(
                """
                INSERT INTO local_proxies (ip, port, user, password, life_time, apply_to, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (ip, port, user or '', password or '', life_time or 0, self._serialize_json(apply_to or [], default_as_list=True), now),
            )
            return cursor.lastrowid

        try:
            return await self.execute_with_retry(_add)
        except Exception as e:
            self.logger.error(f"Error adding local proxy: {e}")
            return None

    async def list_local_proxies(self) -> List[dict]:
        """获取所有本地代理记录"""
        result: List[dict] = []

        async def _list(db):
            async with db.execute("SELECT id, ip, port, user, password, life_time, apply_to, updated FROM local_proxies ORDER BY updated DESC") as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                for r in rows:
                    item = dict(zip(cols, r))
                    item['apply_to'] = self._deserialize_json(item.get('apply_to', '[]'), default_as_list=True)
                    result.append(item)

        try:
            await self.execute_with_retry(_list)
        except Exception as e:
            self.logger.error(f"Error listing local proxies: {e}")
            return None
        return result

    async def update_local_proxy(self, proxy_id: int, **fields) -> Optional[int]:
        """按需更新本地代理字段: 支持 ip, port, user, password, life_time"""
        allowed = {'ip', 'port', 'user', 'password', 'life_time', 'apply_to'}
        to_update = {k: v for k, v in fields.items() if k in allowed}
        if not to_update:
            return None

        if 'apply_to' in to_update:
            to_update['apply_to'] = self._serialize_json(to_update['apply_to'] or [], default_as_list=True)

        set_clause = ', '.join([f"{k} = ?" for k in to_update.keys()]) + ", updated = ?"
        params = list(to_update.values()) + [self._get_utc_timestamp(), proxy_id]

        async def _upd(db):
            await db.execute(f"UPDATE local_proxies SET {set_clause} WHERE id = ?", params)

        try:
            await self.execute_with_retry(_upd)
            return proxy_id
        except Exception as e:
            self.logger.error(f"Error updating local proxy {proxy_id}: {e}")
            return None

    async def delete_local_proxy(self, proxy_id: int) -> Optional[int]:
        """删除指定 id 的本地代理记录"""
        async def _del(db):
            await db.execute("DELETE FROM local_proxies WHERE id = ?", (proxy_id,))

        try:
            await self.execute_with_retry(_del)
            return proxy_id
        except Exception as e:
            self.logger.error(f"Error deleting local proxy {proxy_id}: {e}")
            return None

    # ----------------------- kdl_proxies CRUD -----------------------
    async def add_kdl_proxy(self, SECERT_ID: str, SIGNATURE: str, USER_NAME: str, USER_PWD: str, apply_to: Optional[List[str]] = None) -> Optional[int]:
        """新增一条快代理配置，返回自增id"""
        now = self._get_utc_timestamp()
        async def _add(db):
            cursor = await db.execute(
                """
                INSERT INTO kdl_proxies (SECERT_ID, SIGNATURE, USER_NAME, USER_PWD, apply_to, updated)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (SECERT_ID or '', SIGNATURE or '', USER_NAME or '', USER_PWD or '', self._serialize_json(apply_to or [], default_as_list=True), now),
            )
            return cursor.lastrowid

        try:
            return await self.execute_with_retry(_add)
        except Exception as e:
            self.logger.error(f"Error adding kdl proxy: {e}")
            return None

    async def list_kdl_proxies(self) -> List[dict]:
        """获取所有快代理配置"""
        result: List[dict] = []

        async def _list(db):
            async with db.execute("SELECT id, SECERT_ID, SIGNATURE, USER_NAME, USER_PWD, apply_to, updated FROM kdl_proxies ORDER BY updated DESC") as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                for r in rows:
                    item = dict(zip(cols, r))
                    item['apply_to'] = self._deserialize_json(item.get('apply_to', '[]'), default_as_list=True)
                    result.append(item)

        try:
            await self.execute_with_retry(_list)
        except Exception as e:
            self.logger.error(f"Error listing kdl proxies: {e}")
            return None
        return result

    async def update_kdl_proxy(self, proxy_id: int, **fields) -> Optional[int]:
        """按需更新快代理字段: 支持 SECERT_ID, SIGNATURE, USER_NAME, USER_PWD"""
        allowed = {'SECERT_ID', 'SIGNATURE', 'USER_NAME', 'USER_PWD', 'apply_to'}
        to_update = {k: v for k, v in fields.items() if k in allowed}
        if not to_update:
            return None

        if 'apply_to' in to_update:
            to_update['apply_to'] = self._serialize_json(to_update['apply_to'] or [], default_as_list=True)

        set_clause = ', '.join([f"{k} = ?" for k in to_update.keys()]) + ", updated = ?"
        params = list(to_update.values()) + [self._get_utc_timestamp(), proxy_id]

        async def _upd(db):
            await db.execute(f"UPDATE kdl_proxies SET {set_clause} WHERE id = ?", params)

        try:
            await self.execute_with_retry(_upd)
            return proxy_id
        except Exception as e:
            self.logger.error(f"Error updating kdl proxy {proxy_id}: {e}")
            return None

    async def delete_kdl_proxy(self, proxy_id: int) -> Optional[int]:
        """删除指定 id 的快代理配置"""
        async def _del(db):
            await db.execute("DELETE FROM kdl_proxies WHERE id = ?", (proxy_id,))

        try:
            await self.execute_with_retry(_del)
            return proxy_id
        except Exception as e:
            self.logger.error(f"Error deleting kdl proxy {proxy_id}: {e}")
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
                        self.logger.info(f"Added column '{column_name}' to table '{table_name}'")
                    except Exception as e:
                        self.logger.warning(f"Failed to add column '{column_name}' to table '{table_name}': {str(e)}")
            
            try:
                await self.execute_with_retry(_add_columns)
            except Exception as e:
                self.logger.warning(f"Error adding missing columns to table '{table_name}': {str(e)}")
        
        return updated_columns

    # ---------------------- mc_backup_accounts CRUD ----------------------
    async def add_mc_backup_account(self, platform_name: str, cookies: str) -> Optional[int]:
        """新增一条 mc_backup_accounts 记录，返回自增id"""
        if not platform_name or not cookies:
            self.logger.warning("platform_name and cookies cannot be empty")
            return None
            
        now = self._get_utc_timestamp()
        
        async def _add(db):
            now_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
            account_name = f"{platform_name}_{now_str}"
            
            cursor = await db.execute(
                """
                INSERT INTO mc_backup_accounts (platform_name, account_name, cookies, updated)
                VALUES (?, ?, ?, ?)
                """,
                (platform_name, account_name, cookies, now),
            )
            return cursor.lastrowid

        try:
            return await self.execute_with_retry(_add)
        except Exception as e:
            self.logger.error(f"Error adding mc_backup_account: {e}")
            return None

    async def list_mc_backup_accounts(self, platform_name: Optional[str] = None) -> List[dict]:
        """获取 mc_backup_accounts 记录，可按平台过滤"""
        result: List[dict] = []

        async def _list(db):
            if platform_name:
                query = "SELECT id, platform_name, account_name, cookies, updated FROM mc_backup_accounts WHERE platform_name = ? ORDER BY updated DESC"
                params = (platform_name,)
            else:
                query = "SELECT id, platform_name, account_name, cookies, updated FROM mc_backup_accounts ORDER BY updated DESC"
                params = ()
                
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                for r in rows:
                    item = dict(zip(cols, r))
                    result.append(item)

        try:
            await self.execute_with_retry(_list)
        except Exception as e:
            self.logger.error(f"Error listing mc_backup_accounts: {e}")
            return None
        return result

    async def update_mc_backup_account(self, account_id: int, **fields) -> Optional[int]:
        """按需更新 mc_backup_account 字段: 支持 platform_name, cookies"""
        allowed = {'platform_name', 'cookies'}
        to_update = {k: v for k, v in fields.items() if k in allowed}
        if not to_update:
            return None

        # 如果更新了 platform_name，需要重新生成 account_name
        if 'platform_name' in to_update:
            new_platform_name = to_update['platform_name']
            now_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
            new_account_name = f"{new_platform_name}_{now_str}"
            to_update['account_name'] = new_account_name

        set_clause = ', '.join([f"{k} = ?" for k in to_update.keys()]) + ", updated = ?"
        params = list(to_update.values()) + [self._get_utc_timestamp(), account_id]

        async def _upd(db):
            await db.execute(f"UPDATE mc_backup_accounts SET {set_clause} WHERE id = ?", params)

        try:
            await self.execute_with_retry(_upd)
            return account_id
        except Exception as e:
            self.logger.error(f"Error updating mc_backup_account {account_id}: {e}")
            return None

    async def delete_mc_backup_account(self, account_id: int) -> Optional[int]:
        """删除指定 id 的 mc_backup_account 记录"""
        async def _del(db):
            await db.execute("DELETE FROM mc_backup_accounts WHERE id = ?", (account_id,))

        try:
            await self.execute_with_retry(_del)
            return account_id
        except Exception as e:
            self.logger.error(f"Error deleting mc_backup_account {account_id}: {e}")
            return None

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

    # ---------------------- focuses CRUD ----------------------
    async def get_focus_by_id(self, focus_id: int) -> Optional[dict]:
        """
        根据 id 获取单个 focus 记录
        
        Args:
            focus_id: focus 的 id
            
        Returns:
            Optional[dict]: 成功返回 focus 字典，失败返回None
        """
        async def _get(db):
            async with db.execute(
                "SELECT id, focuspoint, custom_schema, restrictions, explanation, role, purpose, created FROM focuses WHERE id = ?", 
                (focus_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    return result
                return None

        try:
            return await self.execute_with_retry(_get)
        except Exception as e:
            self.logger.error(f"Error getting focus by id {focus_id}: {e}")
            return None

    async def get_focuses_by_ids(self, focus_ids: List[int]) -> List[dict]:
        """
        根据 id 列表批量获取 focus 记录
        
        Args:
            focus_ids: focus id 列表
            
        Returns:
            List[dict]: focus 记录列表
        """
        if not focus_ids:
            return []
            
        result = []
        
        async def _get_batch(db):
            # 构建 IN 查询的占位符
            placeholders = ','.join(['?' for _ in focus_ids])
            query = f"""
                SELECT id, focuspoint, custom_schema, restrictions, explanation, role, purpose 
                FROM focuses 
                WHERE id IN ({placeholders})
            """
            
            async with db.execute(query, focus_ids) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    focus_dict = dict(zip(columns, row))
                    result.append(focus_dict)

        try:
            await self.execute_with_retry(_get_batch)
        except Exception as e:
            self.logger.error(f"Error getting focuses by ids {focus_ids}: {e}")
            return None
            
        return result

    async def list_all_focuses(self) -> List[dict]:
        """
        获取所有 focus 记录
        
        Returns:
            List[dict]: 所有 focus 记录列表，按创建时间倒序
        """
        result = []
        
        async def _list(db):
            async with db.execute(
                "SELECT id, focuspoint, custom_schema, restrictions, explanation, role, purpose, created FROM focuses ORDER BY created DESC"
            ) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    focus_dict = dict(zip(columns, row))
                    result.append(focus_dict)

        try:
            await self.execute_with_retry(_list)
        except Exception as e:
            self.logger.error(f"Error listing all focuses: {e}")
            return None
            
        return result

    async def create_or_update_focus(self, focuspoint: str, restrictions: str = '', explanation: str = '', role: str = '', purpose: str = '', custom_schema: str = '') -> int:
        """
        创建或返回已存在的 focus 记录
        先通过精确查询检查是否存在完全匹配的记录，如果存在则返回已有 focus_id
        只有都不匹配时才创建新记录
        
        Args:
            focuspoint: 焦点内容
            restrictions: 限制条件
            explanation: 解释说明
            role: 角色
            purpose: 目的
            custom_schema: 自定义 schema
            
        Returns:
            int: 已存在或新创建的 focus id
        """
        # 标准化输入
        fp = focuspoint.strip() or ''
        res = restrictions.strip() or ''
        exp = explanation.strip() or ''
        r = role.strip() or ''
        p = purpose.strip() or ''
        cs = custom_schema.strip() or ''

        if not fp and not res:
            self.logger.warning(f"create_or_update_focus: focuspoint/restrictions are all empty, skip")
            return None
        
        # 先通过精确查询检查是否存在完全匹配的记录
        async def _find_existing(db):
            async with db.execute(
                """
                SELECT id FROM focuses 
                WHERE focuspoint = ? 
                  AND restrictions = ? 
                  AND explanation = ? 
                  AND role = ? 
                  AND purpose = ? 
                  AND custom_schema = ?
                LIMIT 1
                """,
                (fp, res, exp, r, p, cs)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        
        # 插入新记录
        async def _insert(db):
            current_time = self._get_utc_timestamp()
            cursor = await db.execute(
                """
                INSERT INTO focuses (focuspoint, custom_schema, restrictions, explanation, role, purpose, created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (fp, cs, res, exp, r, p, current_time),
            )
            return cursor.lastrowid
        
        try:
            # 先查询是否存在
            existing_id = await self.execute_with_retry(_find_existing)
            if existing_id is not None:
                return existing_id
            
            # 不存在则插入新记录
            return await self.execute_with_retry(_insert)
        except Exception as e:
            self.logger.error(f"Error in create_or_update_focus: {e}")
            # 如果插入失败，再次尝试查询（可能是并发插入导致）
            try:
                existing_id = await self.execute_with_retry(_find_existing)
                if existing_id is not None:
                    return existing_id
            except Exception as query_error:
                self.logger.error(f"Error querying existing focus after insert failure: {query_error}")
            # 如果查询也失败，抛出异常
            return None

    # ---------------------- ws_history CRUD ----------------------
    async def add_ws_history(self,
                             type: str,
                             code: int | None = None,
                             params: List[str] | None = None,
                             prompt_id: str | None = None,
                             actions: List[dict] | None = None,
                             action_id: str | None = None,
                             timeout: int | None = None,
                             ts: float | None = None) -> Optional[int]:
        """
        添加一条 websocket 历史消息，存储完整消息字段。
        对于 notify 而言，prompt_id 和 actions 可以为空。
        """
        # Use provided ts (seconds) from producer to keep consistent with frontend broadcast
        # Fall back to current time if not provided
        _ts = float(ts) if ts is not None else time.time()

        async def _add(db):
            cursor = await db.execute(
                """
                INSERT INTO ws_history (type, prompt_id, code, params, actions, action_id, timeout, ts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (type or '').strip(),
                    (prompt_id or '').strip() if prompt_id else None,
                    int(code) if code is not None else None,
                    self._serialize_json(params or [], default_as_list=True),
                    self._serialize_json(actions or [], default_as_list=True),
                    (action_id or '').strip() if action_id else None,
                    int(timeout) if timeout is not None else None,
                    _ts,
                ),
            )
            return cursor.lastrowid

        try:
            return await self.execute_with_retry(_add)
        except Exception as e:
            self.logger.error(f"Error adding ws_history: {e}")
            return None

    async def list_ws_history(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """
        按时间降序分页获取 ws_history 记录。读取前自动清理超过24小时的记录。
        """
        result: List[dict] = []

        async def _cleanup_and_list(db):
            # 清理超过24小时的数据
            cutoff_time = time.time() - 24 * 3600
            try:
                await db.execute("DELETE FROM ws_history WHERE ts < ?", (cutoff_time,))
            except Exception as e:
                # best-effort cleanup
                self.logger.warning(f"Failed to cleanup ws_history: {e}")

            query = (
                """
                SELECT type, prompt_id, code, params, actions, action_id, timeout, ts
                FROM ws_history
                ORDER BY ts DESC
                LIMIT ? OFFSET ?
                """
            )
            params = [limit, offset]
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                for r in rows:
                    item = dict(zip(cols, r))
                    item['params'] = self._deserialize_json(item.get('params', '[]'), default_as_list=True)
                    item['actions'] = self._deserialize_json(item.get('actions', '[]'), default_as_list=True)
                    result.append(item)

        try:
            await self.execute_with_retry(_cleanup_and_list)
        except Exception as e:
            self.logger.error(f"Error listing ws_history: {e}")
            return None
        return result
