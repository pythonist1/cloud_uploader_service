from uuid import UUID, uuid4
from collections import namedtuple
from cloud_uploader_service.domain.use_cases import UploadUseCases
from cloud_uploader_service.domain.model import UploadCase
from cloud_uploader_service.gateway.schemas import CreateUploadCaseData, UploadFilePartData, CompleteUploadData, DeleteUploadData


class FakeRepository:
    def add(self, upload_case):
        pass

    async def get_upload_case_by_reference(self, reference):
        pass

    async def delete_upload_case_record(self, upload_case):
        pass


class FakeUnitOfWork:
    async def __aenter__(self):
        self._repository = FakeRepository()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._repository = None

    @property
    def repository(self):
        return self._repository

    async def commit(self):
        pass


class FakeCloudServiceAdapter:
    async def create_upload(self):
        return uuid4()

    async def upload_part(self, upload_id, part_bytes, part_number):
        pass

    async def complete_upload(self, upload_id):
        pass


async def test_create_upload_case(mocker):
    use_cases = UploadUseCases(cloud_service_adapter=FakeCloudServiceAdapter())

    uow = FakeUnitOfWork()

    cloud_service_create_spy = mocker.spy(FakeCloudServiceAdapter, 'create_upload')
    upload_case_create_spy = mocker.spy(UploadCase, 'create')
    repository_add_spy = mocker.spy(FakeRepository, 'add')
    uow_commit_spy = mocker.spy(FakeUnitOfWork, 'commit')

    data = CreateUploadCaseData(part_amount=2)

    response = await use_cases.create_upload_case(data, uow)

    assert isinstance(response, dict)
    assert response.get('reference')
    assert isinstance(response['reference'], UUID)

    cloud_service_create_spy.assert_awaited()
    upload_case_create_spy.assert_called()
    repository_add_spy.assert_called()
    uow_commit_spy.assert_awaited()


async def test_upload_file_part(mocker):
    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=10)

    async def get_upload_case_by_reference(self, reference):
        return upload_case

    mocker.patch.object(FakeRepository, 'get_upload_case_by_reference', get_upload_case_by_reference)

    upload_case_check_spy = mocker.spy(UploadCase, 'check_part_upload_status')
    upload_case_set_spy = mocker.spy(UploadCase, 'set_part_uploaded')
    cloud_service_adapter_spy = mocker.spy(FakeCloudServiceAdapter, 'upload_part')
    uow_commit_spy = mocker.spy(FakeUnitOfWork, 'commit')

    data = UploadFilePartData(
        reference=upload_case.reference,
        upload_part_bytes=b'bytes'.decode('cp437'),
        upload_part_number=1
    )

    use_cases = UploadUseCases(cloud_service_adapter=FakeCloudServiceAdapter())
    uow = FakeUnitOfWork()

    await use_cases.upload_file_part(data, uow)

    upload_case_check_spy.assert_called()
    upload_case_set_spy.assert_called()
    cloud_service_adapter_spy.assert_awaited()
    uow_commit_spy.assert_awaited()


async def test_complete_upload(mocker):
    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=1)
    upload_case.set_part_uploaded(1)

    async def get_upload_case_by_reference(self, reference):
        return upload_case

    mocker.patch.object(FakeRepository, 'get_upload_case_by_reference', get_upload_case_by_reference)

    upload_case_check_full_upload_spy = mocker.spy(UploadCase, 'check_full_uploaded')
    cloud_service_complete_upload_spy = mocker.spy(FakeCloudServiceAdapter, 'complete_upload')
    delete_upload_record_spy = mocker.spy(FakeRepository, 'delete_upload_case_record')

    data = CompleteUploadData(reference=upload_case.reference)

    use_cases = UploadUseCases(cloud_service_adapter=FakeCloudServiceAdapter())
    uow = FakeUnitOfWork()

    await use_cases.complete_upload_case(data, uow)

    upload_case_check_full_upload_spy.assert_called()
    cloud_service_complete_upload_spy.assert_awaited()
    delete_upload_record_spy.assert_awaited()


async def test_delete_upload_case(mocker):
    delete_upload_record_spy = mocker.spy(FakeRepository, 'delete_upload_case_record')

    data = DeleteUploadData(reference=uuid4())

    use_cases = UploadUseCases(cloud_service_adapter=FakeCloudServiceAdapter())
    uow = FakeUnitOfWork()

    await use_cases.delete_upload_case(data, uow)

    delete_upload_record_spy.assert_awaited()
