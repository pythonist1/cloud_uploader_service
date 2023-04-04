from contextlib import suppress

from cloud_uploader_service.gateway import CreateUploadCaseData, UploadFilePartData, CompleteUploadData, DeleteUploadData
from .abstractions import AbstractCloudServiceAdapter, AbstractUnitOfWork
from .model import UploadCase
from .exceptions import FileAlreadyFullUploaded, FileNotFullUploaded


class UploadUseCases:
    def __init__(self, cloud_service_adapter: AbstractCloudServiceAdapter):
        self._cloud_service_adapter = cloud_service_adapter

    async def create_upload_case(self, data: CreateUploadCaseData, uow: AbstractUnitOfWork) -> dict:
        async with uow:
            cloud_service_id = await self._cloud_service_adapter.create_upload()
            upload_case = UploadCase.create(
                cloud_service_id=cloud_service_id,
                part_amount=data.part_amount
            )
            uow.repository.add(upload_case)
            await uow.commit()
        return {
            'reference': upload_case.reference
        }

    async def upload_file_part(self, data: UploadFilePartData, uow: AbstractUnitOfWork):
        async with uow:
            upload_case = await uow.repository.get_upload_case_by_reference(reference=data.reference)
            upload_case.check_part_upload_status(upload_part_number=data.upload_part_number)
            await self._cloud_service_adapter.upload_part(
                upload_id=upload_case.cloud_service_id,
                part_bytes=data.upload_part_bytes,
                part_number=data.upload_part_number
            )
            upload_case.set_part_uploaded(upload_part_number=data.upload_part_number)
            await uow.commit()

    async def complete_upload_case(self, data: CompleteUploadData, uow: AbstractUnitOfWork):
        async with uow:
            upload_case = await uow.repository.get_upload_case_by_reference(reference=data.reference)
            with suppress(FileAlreadyFullUploaded):
                upload_case.check_full_uploaded()
                raise FileNotFullUploaded('Can not complete upload if file not full uploaded')
            await self._cloud_service_adapter.complete_upload(upload_case.cloud_service_id)
            await uow.repository.delete_upload_case_record(upload_case)

    async def delete_upload_case(self, data: DeleteUploadData, uow: AbstractUnitOfWork):
        async with uow:
            upload_case = await uow.repository.get_upload_case_by_reference(reference=data.reference)
            await uow.repository.delete_upload_case_record(upload_case)
