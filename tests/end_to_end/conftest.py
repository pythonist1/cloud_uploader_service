import aiohttp
import pytest
import logging
import uvicorn
from fastapi import FastAPI

from cloud_uploader_service import bootstrap as btp
from cloud_uploader_service.settings import config

logger = logging.getLogger('gateway_service')


class GatewayService:
    def __init__(self, app: FastAPI, host=None, port=None):
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "loggers": {
                "uvicorn": {},
                "uvicorn.error": {},
                "uvicorn.access": {},
            }
        }
        config = uvicorn.Config(app, host=host or '0.0.0.0', port=port or 8000, log_config=log_config)
        self._server = uvicorn.Server(config)
        self._name = 'HTTP Gateway'


    async def start(self):
        logger.info(f"{self._name} starting")
        try:
            if not self._server.config.loaded:
                self._server.config.load()
            self._server.lifespan = self._server.config.lifespan_class(self._server.config)
            await self._server.startup()
            logger.info(f"{self._name} started")
        except Exception:
            logger.exception(f"{self._name} start fail")
            raise

    async def stop(self, exception: Exception = None):
        await self._server.shutdown()
        if exception:
            logger.error(f'{self._name} finish with error', exc_info=exception)
        else:
            logger.info(f'{self._name} stop')


class ServiceTestClient:
    def __init__(self):
        self._redis_service = btp.bootstrap_redis_service()
        cloud_service_client = btp.bootstrap_cloud_service_client()
        adapter = btp.bootstrap_adapter(cloud_service_client)
        use_case_handler = btp.bootstrap_use_case_handler(self._redis_service, adapter)
        app_config = btp.bootstrap_gateway(use_case_handler)
        app = app_config.get_application()
        self._service = GatewayService(app, app_config.host, app_config.port)

    async def start(self):
        self._redis_service.start()
        await self._redis_service.drop_all()
        await self._service.start()

    async def stop(self):
        await self._redis_service.drop_all()
        await self._redis_service.stop()
        await self._service.stop()

    @classmethod
    async def request(cls, path, data=None):
        async with aiohttp.ClientSession(f'http://{config.gateway_app_host}:{config.gateway_app_port}/') as session:
            async with session.post(path, json=data or {}) as resp:
                status = resp.status
                data = await resp.json(content_type=None)
                return status, data

@pytest.fixture
async def service_test_client():
    client = ServiceTestClient()
    await client.start()
    yield client
    await client.stop()
