from fake_cloud_service_client import CloudServiceClient
from .adapter import CloudServiceAdapter
from .domain import UploadUseCases
from .service_layer import UseCaseHandler, UnitOfWork
from .storage import RedisService, Repository
from .gateway import UploadRoutes, ApplicationConfig
from . import bootstrap_external_services
from .settings import config


def bootstrap_redis_service():
    redis_service = bootstrap_external_services.bootstrap_redis_service()
    return redis_service


def bootstrap_cloud_service_client():
    client = bootstrap_external_services.bootstrap_cloud_service_client()
    return client


def bootstrap_adapter(client: CloudServiceClient):
    adapter = bootstrap_external_services.bootstrap_adapter(client)
    return adapter


def bootstrap_use_case_handler(redis_service: RedisService, adapter: CloudServiceAdapter):
    handler = UseCaseHandler(
        uow_class=UnitOfWork,
        db_service=redis_service,
        repository_class=Repository,
        use_cases_class=UploadUseCases,
        cloud_service_adapter=adapter
    )
    return handler


def bootstrap_gateway(use_case_handler: UseCaseHandler):
    routes = UploadRoutes(use_case_handler)
    app_config = ApplicationConfig()
    app_config.include_router(routes.router, config.gateway_app_host, config.gateway_app_port)
    return app_config
