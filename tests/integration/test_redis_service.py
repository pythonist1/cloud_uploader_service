from uuid import uuid4
from cloud_uploader_service.storage import RedisService
from cloud_uploader_service.settings import config


async def test_redis_service():
    service = RedisService(url=config.redis_url)

    service.start()

    reference = uuid4()

    await service.set(str(reference), {'key': {'1': False}})
    value = await service.get(str(reference))
    assert value == {'key': {'1': False}}

    await service.delete(str(reference))
    value = await service.get(str(reference))
    assert value is None

    await service.set(str(reference), {'key': {'1': False}})
    await service.drop_all()
    value = await service.get(str(reference))
    assert value is None

    await service.stop()
