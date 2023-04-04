import asyncio
from fastapi import APIRouter
from concurrent.futures import ThreadPoolExecutor
from cloud_uploader_service.service_layer.command import Command as command
from cloud_uploader_service.service_layer import UseCaseHandler
from .schemas import ResponseModel, CreateUploadCaseData, UploadFilePartData, CompleteUploadData, DeleteUploadData


class UploadRoutes:
    def __init__(self,
                 use_case_handler: UseCaseHandler,
                 ):
        self._router = APIRouter(prefix='/v1/cloud_uploader')
        self._use_case_handler = use_case_handler
        self._thread_pool_executor = ThreadPoolExecutor()
        self._register_routes()

    @property
    def router(self):
        return self._router

    def _register_routes(self):
        self._router.add_api_route(
            path='/create_upload_case',
            endpoint=self._create_upload_case,
            methods=['POST']
        )
        self._router.add_api_route(
            path='/upload_file_part',
            endpoint=self._upload_file_part,
            methods=['POST']
        )
        self._router.add_api_route(
            path='/complete_upload_case',
            endpoint=self._complete_upload_case,
            methods=['POST']
        )
        self._router.add_api_route(
            path='/delete_upload_case',
            endpoint=self._delete_upload_case,
            methods=['POST']
        )

    async def _create_upload_case(self, data: CreateUploadCaseData):
        response_data = await self._use_case_handler.handle(command.CREATE_UPLOAD_CASE, data)
        return ResponseModel(data=response_data)

    async def _upload_file_part(self, data: UploadFilePartData):
        loop = asyncio.get_running_loop()
        with self._thread_pool_executor as executor:
            await loop.run_in_executor(
                executor,
                self._use_case_handler.handle_upload,
                data
            )
        return ResponseModel()

    async def _complete_upload_case(self, data: CompleteUploadData):
        await self._use_case_handler.handle(command.COMPLETE_UPLOAD_CASE, data)
        return ResponseModel()

    async def _delete_upload_case(self, data: DeleteUploadData):
        await self._use_case_handler.handle(command.DELETE_UPLOAD_CASE, data)
        return ResponseModel()
