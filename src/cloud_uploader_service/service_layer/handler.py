import asyncio

from cloud_uploader_service import domain
from cloud_uploader_service import bootstrap_external_services
from cloud_uploader_service import storage
from .unit_of_work import UnitOfWork


class UseCaseHandler:
    def __init__(self,
                 uow_class,
                 db_service,
                 repository_class,
                 use_cases_class,
                 cloud_service_adapter
                 ):
        self._uow_class = uow_class
        self._db_service = db_service
        self._use_cases = use_cases_class(cloud_service_adapter)
        self._repository_class = repository_class

    def _get_uow(self):
        return self._uow_class(self._db_service, self._repository_class)

    async def handle(self, command, data):
        uow = self._get_uow()
        return await getattr(self._use_cases, command.value)(data=data, uow=uow)

    @classmethod
    def handle_upload(cls, data):
        loop = asyncio.new_event_loop()
        handler, redis_service = cls._bootstrap_handler()
        redis_service.start()
        return loop.run_until_complete(cls._execute_upload_use_case(data, handler, redis_service))

    @staticmethod
    async def _execute_upload_use_case(data, handler, redis_service):
        uow = handler._get_uow()
        await handler._use_cases.upload_file_part(data=data, uow=uow)
        await redis_service.stop()

    @classmethod
    def _bootstrap_handler(cls):
        redis_service = bootstrap_external_services.bootstrap_redis_service()
        client = bootstrap_external_services.bootstrap_cloud_service_client()
        adapter = bootstrap_external_services.bootstrap_adapter(client)
        handler = cls(
            uow_class=UnitOfWork,
            db_service=redis_service,
            repository_class=storage.Repository,
            use_cases_class=domain.UploadUseCases,
            cloud_service_adapter=adapter
        )
        return handler, redis_service
