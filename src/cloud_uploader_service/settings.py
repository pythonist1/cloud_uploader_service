import pathlib
from pydantic import BaseSettings


__all__ = ('config',)


project_path = pathlib.Path(__file__).parent
env_path = str(project_path) + '/.env'


class Config(BaseSettings):
    redis_url: str
    cloud_service_username: str
    cloud_service_password: str
    gateway_app_host: str = '0.0.0.0'
    gateway_app_port: int = 8000


config = Config(_env_file=env_path)
