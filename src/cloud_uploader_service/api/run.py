import uvicorn
from cloud_uploader_service import bootstrap as btp


def run_api():
    redis_service = btp.bootstrap_redis_service()
    redis_service.start()
    cloud_service_client = btp.bootstrap_cloud_service_client()
    adapter = btp.bootstrap_adapter(cloud_service_client)
    use_case_handler = btp.bootstrap_use_case_handler(redis_service, adapter)
    app_config = btp.bootstrap_gateway(use_case_handler)
    app = app_config.get_application()
    uvicorn.run(app, host=app_config.host, port=app_config.port)


if __name__ == '__main__':
    run_api()
