import pickle
import aioredis


class RedisService:
    def __init__(self, url, max_connections=100):
        self._url = url
        self._client = None
        self._max_connections = max_connections

    def start(self):
        self._client = aioredis.from_url(
            url=self._url,
            max_connections=self._max_connections
        )

    async def stop(self):
        await self._client.connection_pool.disconnect()

    async def set(self, key: str, value: dict):
        await self._client.execute_command('set', key, pickle.dumps(value))

    async def get(self, key: str) -> dict | None:
        value = await self._client.execute_command("get", str(key))
        if value is None:
            return
        return pickle.loads(await self._client.execute_command("get", str(key)))

    async def delete(self, key: str):
        await self._client.delete(str(key))

    async def drop_all(self):
        await self._client.flushall()
