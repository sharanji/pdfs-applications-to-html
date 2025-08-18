from app_redis.redis_commands.string_commands import RedisString
from app_redis.redis_commands.list_commands import RedisList
from app_redis.redis_commands.set_commands import RedisSet
from app_redis.redis_commands.hash_commands import RedisHash


class RedisCommandsGenerator:
    def __init__(self):
        pass

    @classmethod
    def get_redis_cmds_generator(cls, redis_client, val_type):

        if val_type == "string":
            return RedisString(redis_client)
        if val_type == "list":
            return RedisList(redis_client)
        if val_type == "set":
            return RedisSet(redis_client)
        if val_type == "hash":
            return RedisHash(redis_client)

        raise Exception("the choice is not present")
