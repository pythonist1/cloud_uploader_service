from cloud_uploader_service.domain import AbstractCloudServiceAdapter
from fake_cloud_service_client.client import CloudServiceClient
from .exceptions import CloudServiceAdapterError


class CloudServiceAdapter(AbstractCloudServiceAdapter):
    def __init__(self, client: CloudServiceClient):
        self._client = client

    async def create_upload(self):
        return await self._client.create_upload()

    async def upload_part(self, upload_id, part_bytes, part_number):
        response = await self._client.upload_file_part(upload_id, part_bytes, part_number)
        if not response['status'] == 'SUCCESS':
            raise CloudServiceAdapterError()

    async def complete_upload(self, upload_id):
        response = await self._client.complete_upload(upload_id)
        if not response['status'] == 'SUCCESS':
            raise CloudServiceAdapterError()
