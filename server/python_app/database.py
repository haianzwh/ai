"""
=============================================================================
  数据库模块
  使用 aiomysql 异步连接池（适配 FastAPI 异步运行）
=============================================================================
"""
import aiomysql
from .config import DB_CONFIG


# 全局连接池（启动时创建）
_pool: aiomysql.Pool | None = None


async def init_db() -> None:
    """
    初始化数据库连接池。
    在 FastAPI 启动事件中调用。
    """
    global _pool
    _pool = await aiomysql.create_pool(**DB_CONFIG)


async def close_db() -> None:
    """
    关闭数据库连接池。
    在 FastAPI 关闭事件中调用，确保优雅退出。
    """
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()


async def get_pool() -> aiomysql.Pool:
    """
    获取连接池实例。如果未初始化则抛出异常。
    供所有数据访问模块调用。
    """
    if _pool is None:
        raise RuntimeError("数据库未初始化！请调用 init_db()")
    return _pool


async def execute(sql: str, params: tuple | list | None = None) -> list[dict]:
    """
    执行 SQL 查询并返回结果列表。
    
    返回格式: [{"column1": value, "column2": value}, ...]
    使用 DictCursor，每条记录自动转为字典，方便后续处理。
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, params or ())
            return await cur.fetchall()


async def execute_one(sql: str, params: tuple | list | None = None) -> dict | None:
    """
    执行 SQL 并返回第一条结果。
    适合查询单条记录（如根据 ID 查用户）。
    """
    rows = await execute(sql, params)
    return rows[0] if rows else None


async def execute_write(sql: str, params: tuple | list | None = None) -> int:
    """
    执行写入 SQL（INSERT/UPDATE/DELETE）并返回影响行数。
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            result = await cur.execute(sql, params or ())
            await conn.commit()
            return result
