import pathlib
import os
import asyncio
from datetime import datetime


path = pathlib.Path(__file__).parent


async def test_create_upload_case(service_test_client):
    redis_service = service_test_client._redis_service

    status, response_data = await service_test_client.request(
        '/v1/cloud_uploader/create_upload_case',
        data={'part_amount': 10}
    )

    assert status == 200
    assert response_data['status'] == 'SUCCESS'

    assert response_data['data'].get('reference')

    reference = response_data['data'].get('reference')

    data = await redis_service.get(reference)

    assert data['part_amount'] == 10

    upload_part_numbers = list()
    for part_number in range(1, data['part_amount'] + 1):
        part_number_data = await redis_service.get(f'{reference}_{part_number}')
        if part_number_data:
            upload_part_numbers.append(part_number)

    assert len(upload_part_numbers) == 10


async def test_upload_part(service_test_client):
    redis_service = service_test_client._redis_service

    file_path = pathlib.Path.joinpath(path, 'img.png')
    stats = os.stat(file_path)

    full_parts_amount = stats.st_size // 10000
    remainder = stats.st_size % 10000

    part_amount = full_parts_amount
    if remainder > 0:
        part_amount += 1

    status, response_data = await service_test_client.request(
        '/v1/cloud_uploader/create_upload_case',
        data={'part_amount': part_amount}
    )

    reference = response_data['data'].get('reference')

    async def send_file_part(bytes, part_number):
        data = {
            'reference': reference,
            'upload_part_bytes': bytes.decode('cp437'),
            'upload_part_number': part_number
        }

        status, response_data = await service_test_client.request(
            '/v1/cloud_uploader/upload_file_part',
            data=data
        )

        assert status == 200
        assert response_data['status'] == 'SUCCESS'

    async_tasks = list()

    start_time = datetime.now()

    with open(file_path, 'rb') as fp:
        for i in range(full_parts_amount):
            im_b = fp.read(10000)
            task = asyncio.create_task(send_file_part(im_b, i + 1))
            async_tasks.append(task)
        im_b = fp.read(stats.st_size % 10000)
        task = asyncio.create_task(send_file_part(im_b, full_parts_amount + 1))
        async_tasks.append(task)

    exceptions = await asyncio.gather(*async_tasks, return_exceptions=True)

    for i in exceptions:
        assert i == None

    end_time = datetime.now()

    timedelta = end_time - start_time

    assert timedelta.seconds < 11

    data = await redis_service.get(reference)

    assert data['reference'] == reference
    assert data['part_amount'] == 4

    success_uploads = list()
    for part_number in range(1, data['part_amount'] + 1):
        part_number_data = await redis_service.get(f'{reference}_{part_number}')
        if part_number_data['status']:
            success_uploads.append(part_number)

    assert len(success_uploads) == 4


async def test_complete_upload(service_test_client):
    redis_service = service_test_client._redis_service

    file_path = pathlib.Path.joinpath(path, 'img.png')
    stats = os.stat(file_path)

    full_parts_amount = stats.st_size // 10000
    remainder = stats.st_size % 10000

    part_amount = full_parts_amount
    if remainder > 0:
        part_amount += 1

    status, response_data = await service_test_client.request(
        '/v1/cloud_uploader/create_upload_case',
        data={'part_amount': part_amount}
    )

    reference = response_data['data'].get('reference')

    async def send_file_part(bytes, part_number):
        data = {
            'reference': reference,
            'upload_part_bytes': bytes.decode('cp437'),
            'upload_part_number': part_number
        }

        status, response_data = await service_test_client.request(
            '/v1/cloud_uploader/upload_file_part',
            data=data
        )

        assert status == 200
        assert response_data['status'] == 'SUCCESS'

    async_tasks = list()

    with open(file_path, 'rb') as fp:
        for i in range(full_parts_amount):
            im_b = fp.read(10000)
            task = asyncio.create_task(send_file_part(im_b, i + 1))
            async_tasks.append(task)
        im_b = fp.read(stats.st_size % 10000)
        task = asyncio.create_task(send_file_part(im_b, full_parts_amount + 1))
        async_tasks.append(task)

    exceptions = await asyncio.gather(*async_tasks, return_exceptions=True)

    for i in exceptions:
        assert i == None

    status, response_data = await service_test_client.request(
        '/v1/cloud_uploader/complete_upload_case',
        data={'reference': reference}
    )

    assert status == 200
    assert response_data['status'] == 'SUCCESS'

    data = await redis_service.get(reference)

    assert data == None

    for part_number in range(1, 10 + 1):
        data = await redis_service.get(f'{reference}_{part_number}')
        assert data == None


async def test_delete_upload_case(service_test_client):
    redis_service = service_test_client._redis_service

    status, response_data = await service_test_client.request(
        '/v1/cloud_uploader/create_upload_case',
        data={'part_amount': 10}
    )

    assert status == 200

    reference = response_data['data'].get('reference')

    status, response_data = await service_test_client.request(
        '/v1/cloud_uploader/delete_upload_case',
        data={'reference': reference}
    )

    assert status == 200
    assert response_data['status'] == 'SUCCESS'

    data = await redis_service.get(reference)

    assert data == None

    for part_number in range(1, 10 + 1):
        data = await redis_service.get(f'{reference}_{part_number}')
        assert data == None
