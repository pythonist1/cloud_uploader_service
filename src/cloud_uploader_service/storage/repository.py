from uuid import UUID

from cloud_uploader_service.domain import AbstractRepository
from cloud_uploader_service.domain import model
from .exceptions import UploadCaseNotFound, UploadPartStatusNotFound
from .redis_service import RedisService

UploadCase = model.UploadCase


class Repository(AbstractRepository):
    def __init__(self, redis_service: RedisService):
        self._redis_service = redis_service
        self._seen = set()

    async def get_upload_case_by_reference(self, reference: UUID) -> UploadCase:
        data = await self._redis_service.get(str(reference))
        if not data:
            raise UploadCaseNotFound('Upload case not found in storage')
        upload_part_statuses = await self._get_upload_part_statuses(data)
        data['upload_part_statuses'] = upload_part_statuses
        upload_case = Converter.convert_data_to_upload_case(data)
        self._seen.add(upload_case)
        return upload_case

    async def _get_upload_part_statuses(self, data):
        upload_part_statuses = dict()
        for part_number in range(1, data['part_amount'] + 1):
            status = await self._get_part_status(data['reference'], part_number)
            upload_part_statuses[part_number] = status
        return upload_part_statuses

    async def _get_part_status(self, reference, part_number):
        data = await self._redis_service.get(f'{reference}_{part_number}')
        if not data:
            raise UploadPartStatusNotFound('Upload part status not found in storage')
        return data['status']

    async def _add_to_storage(self, upload_case: UploadCase) -> None:
        data = Converter.convert_upload_case_to_data(upload_case)
        await self._redis_service.set(key=data['reference'], value=data)
        if upload_case._new_case:
            await self._save_part_statuses(upload_case)
        else:
            await self._save_actual_part_status(upload_case)

    async def _save_part_statuses(self, upload_case: UploadCase):
        for key in upload_case._upload_part_statuses.keys():
            await self._redis_service.set(key=f'{upload_case.reference}_{key}', value={'status': False})

    async def _save_actual_part_status(self, upload_case: UploadCase):
        actual_part = upload_case._actual_part
        status = upload_case._upload_part_statuses[actual_part]
        await self._redis_service.set(key=f'{upload_case.reference}_{actual_part}', value={'status': status})

    async def delete_upload_case_record(self, upload_case: UploadCase):
        await self._redis_service.delete(upload_case.reference)
        for part_number in range(1, upload_case._part_amount + 1):
            await self._redis_service.delete(f'{upload_case.reference}_{part_number}')

    def add(self, upload_case: model.UploadCase) -> None:
        self._seen.add(upload_case)


class Converter:
    def convert_upload_case_to_data(upload_case: UploadCase):
        data = {
            'reference': str(upload_case.reference),
            'cloud_service_id': upload_case.cloud_service_id,
            'part_amount': upload_case._part_amount
        }
        return data

    def convert_data_to_upload_case(data: dict):
        upload_case = model.UploadCase.restore(
            reference=UUID(data['reference']),
            cloud_service_id=data['cloud_service_id'],
            part_amount=data['part_amount'],
            upload_part_statuses=data['upload_part_statuses']
        )
        return upload_case
