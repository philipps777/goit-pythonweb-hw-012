import redis.asyncio as redis
from src.conf.config import config

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(config.REDIS_URL)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        await self.redis.set(key, value, ex=ex)

    async def delete(self, key: str):
        await self.redis.delete(key)
