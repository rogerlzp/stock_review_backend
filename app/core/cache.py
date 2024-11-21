from redis import Redis
from fastapi import Depends
from functools import lru_cache
import json
from typing import Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        try:
            self.redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

        self.default_expire = settings.CACHE_EXPIRE

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存数据"""
        try:
            self.redis_client.set(
                key,
                json.dumps(value),
                ex=expire or self.default_expire
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False

    async def clear_prefix(self, prefix: str) -> bool:
        """清除指定前缀的所有缓存"""
        try:
            keys = self.redis_client.keys(f"{prefix}:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis clear_prefix error: {str(e)}")
            return False

@lru_cache()
def get_cache() -> RedisCache:
    return RedisCache() 