import logging

from app_redis.pickle_helper import Pickle_Helper
from app_redis.redis_exceptions import RedisKeyError, RedisResponseError, RedisDataTypeError, RedisSyntaxError
from app_redis.utils import is_int_value, check_val_type

from .base_commands import RedisBase


class RedisHash(RedisBase):
    """
        Redis Hash Commands
    """

    def __init__(self, redis_client):
        super(RedisHash, self).__init__(redis_client)
        self.type = "hash"

    def get(self, key):
        """
        Method to get the complete key-value pairs of ``key``
        Parameters:
            key: redis key
        Returns:
            dict: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.get("map") --> {"alpha": "A", "beta": "B"}
        """
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return {}
        return Pickle_Helper.deserialize_dict(self.redis_client.hgetall(key))

    def set(self, key, value, secs=None, millisecs=None):
        """
        Method to set key and key-value pair mapping into db. Returns True when successfully set
        Parameters:
            key: redis key
            value: redis mapping value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            redis_hash = redis_client("hash")

            type 1: redis_hash.set("map", {"alpha": "A", "beta": "B"}) --> True

            type 2: redis_hash.set("map", {"alpha": "A", "beta": "B"}, secs=120)  --> True

            type 3: redis_hash.set("map", {"alpha": "A", "beta": "B"}, millisecs=4000)  --> True
        """
        try:
            value = Pickle_Helper.serialize_dict(value)
            response = self.redis_client.hset(key, mapping=value) > 0
            return self.set_expire(key, secs, millisecs) and response
        except Exception as exc:
            logging.exception("RedisHash: Set operation failed due to %s", str(exc))
            return None

    def update(self, key, value, secs=None, millisecs=None):
        """
        Method to update key-value pair. Returns True when successfully updated
        Parameters:
            key: redis key
            value: redis mapping value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            redis_hash = redis_client("hash")

            type 1: redis_hash.update("map", {"alpha": "A", "beta": "B"}) --> True

            type 2: redis_hash.update("map", {"alpha": "A", "beta": "B"}, secs=120)  --> True

            type 3: redis_hash.update("map", {"alpha": "A", "beta": "B"}, millisecs=4000)  --> True
        """
        try:
            value = Pickle_Helper.serialize_dict(value)
            if not self.exists(key):
                err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
                logging.info(err_msg)
                return False
            self.delete(key)
            response = self.redis_client.hset(key, mapping=value) > 0
            return self.set_expire(key, secs, millisecs) and response
        except Exception as exc:
            logging.exception("RedisHash: Update operation failed due to %s", str(exc))
            return False

    def get_field(self, key, field):
        """
        Method to return the value of ``field`` within the hash ``key``
        Parameters:
            key: redis key
            field: redis field for key
        Returns:
            str: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.get("map", "alpha") --> "A"
        """
        field = Pickle_Helper.serialize_value(field)
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        if not self.redis_client.hexists(key, field):
            err_msg = "RedisHash: Field Not Found. Provided field does not exists in cache."
            logging.info(err_msg)
            return None

        feild_value = self.redis_client.hget(key, field)
        return Pickle_Helper.deserialize_value(feild_value)

    def set_field(self, key, field, value):
        """
        Method to set the ``value`` of ``field`` within the hash ``key``. If ``field`` is present then new ``value`` is
        set. If ``field`` is NOT present then new field-value pair created.
        In case ``key`` is NOT present then new key with field-value pair created
        Parameters:
            key: redis key
            field: redis field for key
            value: value corresponding to field
        Returns:
            boolean: response
        Examples:
            redis_hash = redis_client("hash")

            type 1: redis_hash.set("map", "alpha", "C") --> True

            type 2: redis_hash.set("map", "omega", "O") --> True

            type 3: redis_hash.set("map_new", "omega", "O") --> True
        """
        field = Pickle_Helper.serialize_value(field)
        value = Pickle_Helper.serialize_value(value)
        return self.redis_client.hset(key, field, value) > 0

    def del_field(self, key, *fields):
        """
        Method to delete the ``fields`` within the hash ``key``
        Parameters:
            key: redis key
            fields: redis field for key
        Returns:
            boolean: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.del_field("map", "alpha") -->  True
        """
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False

        fields = Pickle_Helper.serialize_list(list(fields))
        response = self.redis_client.hdel(key, *fields) > 0
        if not response:
            err_msg = "RedisHash: Field Not Found. Provided field does not exists in cache."
            logging.info(err_msg)
            return False
        return response

    def field_exists(self, key, field):
        """
        Method to check the value of ``field`` exists within the hash ``key``
        Parameters:
            key: redis key
            field: redis field for key
        Returns:
            boolean: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.del_field("map", "beta") -->  True
        """
        field = Pickle_Helper.serialize_value(field)
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        return self.redis_client.hexists(key, field)

    def field_increment_by(self, key, field, increment=1):
        """
        Method to increment the value of ``field`` in hash ``key`` by ``increment``
        Parameters:
            key: redis key
            field: redis field for key
            increment (int): increment amount (default: 1)
        Returns:
            int: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.set("counter", "inc", 1)

            type 1: redis_hash.field_increment_by("counter", "inc")  -->  2

            type 2: redis_hash.field_increment_by("counter", "inc", 2)  -->  4
        """
        field = Pickle_Helper.serialize_value(field)
        old_val = Pickle_Helper.deserialize_value(self.redis_client.hget(key, field))
        if check_val_type(increment, int):
            return None
        if self.exists(key) and self.redis_client.hexists(key, field) and not is_int_value(old_val):
            err_msg = "RedisHash: Value Error. Value is not an integer or out of range."
            logging.exception(err_msg)
            return None
        incremented_val = old_val + increment
        self.redis_client.hset(key, field, Pickle_Helper.serialize_value(incremented_val))
        return self.redis_client.hget(key, field)

    def field_decrement_by(self, key, field, decrement=1):
        """
        Method to increment the value of ``field`` in hash ``key`` by ``increment``
        Parameters:
            key: redis key
            field: redis field for key
            decrement (int): decrement amount (default: 1)
        Returns:
            int: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.set("counter", "dec", 10)

            type 1: redis_hash.field_decrement_by("counter", "dec")  -->  9

            type 2: redis_hash.field_decrement_by("counter", "dec", 2)  -->  8
        """
        field = Pickle_Helper.serialize_value(field)
        if check_val_type(decrement, int):
            return None
        if self.exists(key) and self.redis_client.hexists(key, field) \
                and not is_int_value(self.redis_client.hget(key, field)):
            err_msg = "RedisHash: Value Error. Value is not an integer or out of range."
            logging.exception(err_msg)
            return None
        return self.redis_client.hincrby(key, field, (-1) * decrement)

    def get_length(self, key):
        """
        Method to return the number of elements in hash ``key``
        Parameters:
            key: redis key
        Returns:
            int: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.set("map", {"alpha": "A", "beta": "B"})

            redis_hash.get_length("map")  -->  2
        """
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return 0
        return self.redis_client.hlen(key)

    def hash_keys(self, key):
        """
        Method to return the number of elements in hash ``key``
        Parameters:
            key: redis key
        Returns:
            int: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.set("map", {"alpha": "A", "beta": "B"})

            redis_hash.hash_keys("map")  -->  ["alpha", "beta"]
        """
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return []
        return Pickle_Helper.deserialize_list(self.redis_client.hkeys(key))

    def hash_vals(self, key):
        """
        Method to return the number of elements in hash ``key``
        Parameters:
            key: redis key
        Returns:
            int: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.set("map", {"alpha": "A", "beta": "B"})

            redis_hash.hash_vals("map")  -->  ["A", "B"]
        """
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return []
        return Pickle_Helper.deserialize_list(self.redis_client.hvals(key))

    def field_str_len(self, key, field):
        """
        Method to length of ``field`` value in hash ``key``
        Parameters:
            key: redis key
            field: redis field for key
        Returns:
            int: response
        Examples:
            redis_hash = redis_client("hash")

            redis_hash.set("map", {"alpha": "A", "beta": "B"})

            redis_hash.field_str_len("map")  -->  1
        """
        field = Pickle_Helper.serialize_value(field)
        if not self.exists(key):
            err_msg = "RedisHash: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return 0
        if not self.redis_client.hexists(key, field):
            err_msg = "RedisHash: Field Not Found. Provided field does not exists in cache."
            logging.info(err_msg)
            return 0

        return self.redis_client.hstrlen(key, field)
