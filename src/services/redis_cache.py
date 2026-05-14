import pickle

import redis.asyncio as redis

from src.conf.config import config

redis_client = redis.from_url(
    config.REDIS_URL,
    decode_responses=False,
)


async def get_cache(key: str):
    cached_data = await redis_client.get(key)

    if cached_data is None:
        return None

    return pickle.loads(cached_data)


async def set_cache(key: str, value, expire: int = 900):
    await redis_client.set(
        key,
        pickle.dumps(value),
        ex=expire,
    )


async def delete_cache(key: str):
    await redis_client.delete(key)
