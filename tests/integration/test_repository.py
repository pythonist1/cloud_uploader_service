import pytest
from uuid import uuid4
from cloud_uploader_service.service_layer import UnitOfWork
from cloud_uploader_service.storage.redis_service import RedisService
from cloud_uploader_service.storage import Repository, exceptions
from cloud_uploader_service.domain.model import UploadCase
from cloud_uploader_service.settings import config


@pytest.fixture()
async def redis_client():
    redis_service = RedisService(url=config.redis_url)
    redis_service.start()
    await redis_service.drop_all()
    yield redis_service
    await redis_service.drop_all()
    await redis_service.stop()


async def test_repository_add_upload_case(redis_client):
    uow = UnitOfWork(redis_client, Repository)

    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=10)

    async with uow:
        uow.repository.add(upload_case)
        await uow.commit()

    value = await redis_client.get(str(upload_case.reference))

    upload_case_data = {
        'reference': str(upload_case.reference),
        'cloud_service_id': upload_case.cloud_service_id,
        'part_amount': 10
    }

    assert value == upload_case_data

    upload_part_statuses = dict()
    for part_number in range(1, 10 + 1):
        data = await redis_client.get(f'{upload_case.reference}_{part_number}')
        upload_part_statuses[part_number] = data['status']

    assert upload_part_statuses == {part_number: False for part_number in range(1, 11)}


async def test_repository_get_upload_case(redis_client):
    uow = UnitOfWork(redis_client, Repository)

    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=10)

    async with uow:
        uow.repository.add(upload_case)
        await uow.commit()

    async with uow:
        upload_case_from_storage = await uow.repository.get_upload_case_by_reference(upload_case.reference)

    assert upload_case_from_storage.cloud_service_id == upload_case.cloud_service_id
    assert upload_case_from_storage._part_amount == upload_case._part_amount
    assert upload_case_from_storage._upload_part_statuses == upload_case._upload_part_statuses


async def test_repository_get_upload_case_if_not_found(redis_client):
    uow = UnitOfWork(redis_client, Repository)

    with pytest.raises(exceptions.UploadCaseNotFound):
        async with uow:
            await uow.repository.get_upload_case_by_reference(uuid4())


async def test_repository_delete_record(redis_client):
    uow = UnitOfWork(redis_client, Repository)

    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=10)

    async with uow:
        uow.repository.add(upload_case)
        await uow.commit()

    async with uow:
        upload_case_from_storage = await uow.repository.get_upload_case_by_reference(upload_case.reference)

    assert upload_case_from_storage.reference == upload_case.reference

    async with uow:
        await uow.repository.delete_upload_case_record(upload_case)

    with pytest.raises(exceptions.UploadCaseNotFound):
        async with uow:
            await uow.repository.get_upload_case_by_reference(upload_case.reference)

    for part_number in range(1, 10 + 1):
        data = await redis_client.get(f'{upload_case.reference}_{part_number}')
        assert data == None
