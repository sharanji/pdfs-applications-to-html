from .utils import setup_redis_client
from .redis_commands_generator import RedisCommandsGenerator


class RedisClient():
    """
    Redis Client Interface

    Examples to call the interface

    type 1: redis_client = RedisClient()
            list_redis = redis_client("list")   # initialize redis by calling redis data-type
            list_redis.get("dummy")

    type 2: redis_client = RedisClient()
            redis_client("hash").delete("sample")   # using python inline we can do the same
    """

    def __init__(self):
        self.redis_client = setup_redis_client()

    def __call__(self, _type):
        """
        Call function to initialize redis data-type
        Parameters:
            _type: data-type (string / list / set / hash)
        Returns:
            RedisBaseCommands
        """
        return RedisCommandsGenerator.get_redis_cmds_generator(self.redis_client, _type)
