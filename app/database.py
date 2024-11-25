from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from loguru import logger

# 添加数据库查询监听器
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.debug("Executing query:")
    logger.debug(f"Statement: {statement}")
    logger.debug(f"Parameters: {parameters}")

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=60,  # 增加超时时间
        pool_recycle=1800,
        pool_pre_ping=True,  # 添加连接检查
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        },
        echo=True  # 启用 SQL 日志
    )
    
    # 注册查询监听器
    event.listen(engine, 'before_cursor_execute', before_cursor_execute)
    
    logger.info("Successfully connected to the database")
except Exception as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()