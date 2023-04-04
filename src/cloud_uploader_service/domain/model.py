from uuid import UUID, uuid4
from .exceptions import FileAlreadyFullUploaded, FilePartAlreadyUploaded


class UploadCase:
    _reference: UUID
    _cloud_service_id: UUID
    _part_amount: int
    _upload_part_statuses: dict
    _is_full_uploaded: bool
    _actual_part: int
    _new_case: bool

    @classmethod
    def create(cls, cloud_service_id: str, part_amount: int) -> 'UploadCase':
        self = cls()
        self._reference = uuid4()
        self._cloud_service_id = cloud_service_id
        self._part_amount = part_amount
        self._upload_part_statuses = {part_number: False for part_number in range(1, part_amount + 1)}
        self._actual_part = None
        self._new_case = True
        return self

    @classmethod
    def restore(cls,
                reference: UUID,
                cloud_service_id: str,
                part_amount: int,
                upload_part_statuses: dict,
                ) -> 'UploadCase':
        self = cls()
        self._reference = reference
        self._cloud_service_id = cloud_service_id
        self._part_amount = part_amount
        self._upload_part_statuses = upload_part_statuses
        self._actual_part = None
        self._new_case = False
        return self

    @property
    def reference(self):
        return self._reference

    @property
    def cloud_service_id(self):
        return self._cloud_service_id

    def check_part_upload_status(self, upload_part_number: int):
        if self._upload_part_statuses[upload_part_number]:
            raise FilePartAlreadyUploaded('File part is already uploaded')

    def check_full_uploaded(self):
        if all(self._upload_part_statuses.values()):
            raise FileAlreadyFullUploaded('File is already full uploaded')

    def set_part_uploaded(self, upload_part_number: int):
        self._actual_part = upload_part_number
        self._upload_part_statuses[upload_part_number] = True
