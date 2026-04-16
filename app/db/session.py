# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# 1. 创建异步引擎
# echo=True: 会在控制台打印生成的 SQL 语句，方便调试（生产环境设为 False）
# create_async_engine 是 SQLAlchemy 1.4+ 中用于创建异步引擎的方法
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, 
    pool_pre_ping=True, # 自动检测连接是否失效并重连
    pool_size=10,       # 连接池大小
    max_overflow=20     # 允许超过池大小的最大连接数
)

# 2. 创建异步会话工厂
# class_=AsyncSession: 指定生成的会话类是异步的
# expire_on_commit=False: 提交后不使属性过期，避免一些异步上下文问题
# async_sessionmaker 是 SQLAlchemy 1.4+ 中推荐的异步会话工厂方法
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. 获取数据库会话的依赖函数 (稍后在 API 中使用)
# 这是一个生成器，使用 yield 而不是 return
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db  # 将会话提供给 API 使用
    finally:
        await db.close() # 无论成功失败，最后都要关闭连接