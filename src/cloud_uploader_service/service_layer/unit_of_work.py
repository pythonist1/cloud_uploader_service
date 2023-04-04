

class UnitOfWork:
    def __init__(self, db_client, respository_class):
        self._db_client = db_client
        self._repository_class = respository_class
        self._repository = None

    @property
    def repository(self):
        return self._repository

    async def __aenter__(self):
        self._repository = self._repository_class(self._db_client)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._repository = None

    async def commit(self):
        for entity in self._repository._seen:
            await self._repository._add_to_storage(entity)
