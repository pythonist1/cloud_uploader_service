import pytest
from uuid import UUID, uuid4
from cloud_uploader_service.domain.model import UploadCase, FilePartAlreadyUploaded, FileAlreadyFullUploaded



def test_create_upload_case():
    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=10)

    assert isinstance(upload_case.reference, UUID)
    assert upload_case.cloud_service_id == cloud_service_id
    assert upload_case._upload_part_statuses == {part_number: False for part_number in range(1, 11)}


def test_restore_upload_case():
    cloud_service_id = str(uuid4())
    upload_case = UploadCase.create(cloud_service_id=cloud_service_id, part_amount=2)
    upload_case.check_part_upload_status(1)

    upload_case.set_part_uploaded(1)

    with pytest.raises(FilePartAlreadyUploaded):
        upload_case.check_part_upload_status(1)

    upload_case_restored = UploadCase.restore(
        reference=upload_case.reference,
        cloud_service_id=upload_case.cloud_service_id,
        part_amount=2,
        upload_part_statuses=upload_case._upload_part_statuses
    )

    assert upload_case_restored.cloud_service_id == upload_case.cloud_service_id
    assert upload_case_restored._part_amount == upload_case._part_amount
    assert upload_case_restored._upload_part_statuses == upload_case._upload_part_statuses

    with pytest.raises(FilePartAlreadyUploaded):
        upload_case_restored.check_part_upload_status(1)

    upload_case_restored.check_part_upload_status(2)

    upload_case_restored.set_part_uploaded(2)

    with pytest.raises(FileAlreadyFullUploaded):
        upload_case_restored.check_full_uploaded()
