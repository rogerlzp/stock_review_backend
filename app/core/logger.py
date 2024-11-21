import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

# 日志文件路径
LOG_PATH = Path("logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)

# 日志格式
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# 配置 loguru
logger.remove()  # 删除默认处理器
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=settings.LOG_LEVEL,
    colorize=True
)
logger.add(
    LOG_PATH / "app.log",
    format=LOG_FORMAT,
    level=settings.LOG_LEVEL,
    rotation="100 MB",
    retention="14 days",
)

# 配置 SQLAlchemy 日志
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# 替换所有的 logging 处理器
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True) 