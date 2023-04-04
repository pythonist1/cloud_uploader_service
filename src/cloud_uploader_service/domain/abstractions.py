from uuid import UUID
from abc import ABC, abstractmethod
from typing import Protocol
from .model import UploadCase


class AbstractRepository(ABC):
    @abstractmethod
    async def get_upload_case_by_reference(self, reference: UUID) -> UploadCase:
        pass

    @abstractmethod
    async def delete_upload_case_record(self, upload_case: UploadCase) -> None:
        pass

    @abstractmethod
    def add(self, upload_case: UploadCase) -> None:
        pass

    @abstractmethod
    async def _add_to_storage(self, upload_case: UploadCase) -> None:
        pass


class AbstractCloudServiceAdapter(ABC):
    @abstractmethod
    async def create_upload(self):
        pass

    @abstractmethod
    async def upload_part(self, upload_id: str, part_bytes: bytes, part_number: int):
        pass

    @abstractmethod
    async def complete_upload(self, upload_id: str):
        pass


class AbstractUnitOfWork(Protocol):
    @property
    def repository(self) -> AbstractRepository:
        pass

    async def commit(self) -> None:
        pass
