import time
from uuid import uuid4
import asyncio


class CloudServiceClient:
    def __init__(self, username, password, block_time=10):
        self._username = username
        self._password = password
        self._block_time = block_time

    async def create_upload(self):
        return str(uuid4())

    async def upload_file_part(self, upload_id, fyle_part_bytes, part_number):
        time.sleep(self._block_time)
        return {'status': 'SUCCESS'}

    async def complete_upload(self, upload_id):
        return {'status': 'SUCCESS'}
