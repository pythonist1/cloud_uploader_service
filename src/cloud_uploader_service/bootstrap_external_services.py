from fake_cloud_service_client import CloudServiceClient
from . import adapter as a
from .storage import RedisService
from .settings import config


def bootstrap_redis_service():
    redis_service = RedisService(url=config.redis_url)
    return redis_service


def bootstrap_cloud_service_client():
    client = CloudServiceClient(username=config.cloud_service_username, password=config.cloud_service_password)
    return client


def bootstrap_adapter(client: CloudServiceClient):
    adapter = a.CloudServiceAdapter(client=client)
    return adapter
