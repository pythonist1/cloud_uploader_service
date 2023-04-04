import logging

from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse

from cloud_uploader_service.base_exception import BaseCloudUploaderException


async def base_exception_handler(app, request: Request, exc: Exception):
    logging.getLogger('gateway').error('Internal service error', exc_info=exc, extra={'path': request.url.path})
    return JSONResponse(
        status_code=200,
        content={
            'status': "ERROR",
            'data': {},
            'exc_code': 'InternalServiceError',
            'exc_data': {},
            'message': repr(exc),
        }
    )


async def base_cloud_uploader_exception(app, request: Request, exc: BaseCloudUploaderException):
    return JSONResponse(
        status_code=200,
        content={
            'status': "ERROR",
            'data': {},
            'exc_code': type(exc).__name__,
            'exc_data': {},
            'message': exc.message,
        }
    )


class ApplicationConfig:
    BASE_EXCEPTION_HANDLER = base_exception_handler
    BASE_CLOUD_UPLOADER_EXCEPTION_HANDLER = base_cloud_uploader_exception

    def __init__(self):
        self._routers = list()

    def include_router(self, router: APIRouter, host: str, port: int):
        self._routers.append(router)
        self.host = host
        self.port = port

    def get_application(self) -> FastAPI:
        app = FastAPI()

        app.add_exception_handler(Exception, self.BASE_EXCEPTION_HANDLER)
        app.add_exception_handler(BaseCloudUploaderException, self.BASE_CLOUD_UPLOADER_EXCEPTION_HANDLER)

        for router in self._routers:
            app.include_router(router)

        return app
