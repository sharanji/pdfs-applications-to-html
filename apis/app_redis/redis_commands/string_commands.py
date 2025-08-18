import logging

from app_redis.redis_exceptions import RedisKeyError, RedisResponseError, RedisSyntaxError
from app_redis.utils import decode_byte_to_str, is_valid, is_int_value, check_val_type
from .base_commands import RedisBase


class RedisString(RedisBase):
    """
    Redis String Commands
    """

    def __init__(self, redis_client):
        super(RedisString, self).__init__(redis_client)
        self.type = "string"

    def get(self, key):
        """
        Method to get the value corresponding to given key
        Parameters:
            key: redis key
        Returns:
            str: string value
        Examples:
            str_redis = redis_client("string")

            str_redis.get("name") --> "dummy"
        """
        if self.check_valid_key(key) and not self.exists(key):
            err_msg = "RedisString: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return ""
        return decode_byte_to_str(self.redis_client.get(key))

    def set(self, key, value, secs=None, millisecs=None):
        """
        Method to set key-value pair into db. Returns True when successfully set
        Parameters:
            key: redis key
            value: redis value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            str_redis = redis_client("string")

            type 1: str_redis.set("name", "dummy")  --> True

            type 2: str_redis.set("name", "dummy", secs=120)  --> True

            type 3: str_redis.set("name", "dummy", millisecs=4000)  --> True
        """
        if not self.check_valid_key_value(key, value):
            return False

        if secs and millisecs:
            err_msg = "RedisString: Syntax Error. Set expire time either in seconds or milliseconds."
            logging.info(err_msg)
            return False
        return self.redis_client.set(key, value, secs, millisecs)

    def update(self, key, value, secs=None, millisecs=None):
        """
        Method to update key-value pair. Returns True when successfully updated
        Parameters:
            key: redis key
            value: redis value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            str_redis = redis_client("string")

            str_redis.update("name", "dummy", secs=150) --> True
        """
        if not self.exists(key):
            err_msg = "RedisString: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        return self.set(key, value, secs, millisecs)

    def append_value(self, key, value):
        """
        Method to append string value to the value at key. If key does not exist, create
        new key-value pair. Returns True when successfully append
        Parameters:
            key: redis key
            value: redis value
        Returns:
            string: new redis value
        Examples:
            str_redis = redis_client("string")

            str_redis.set("name", "dummy")

            str_redis.append_value("name", " response") --> "dummy response"
        """
        response = None
        if self.check_valid_key(key) and is_valid(value) and self.redis_client.append(key, value) > -1:
            response = self.get(key)
        return response

    def get_and_delete(self, key):
        """
        Method to get value corresponding to given key and delete the key. If key doesn't exist throws RedisKeyError
        Parameters:
            key: redis key
        Returns:
            string: value at key
        Examples:
            str_redis = redis_client("string")

            str_redis.get_and_delete("name") --> True
        """
        if self.check_valid_key(key) and not self.exists(key):
            err_msg = "RedisString: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        return decode_byte_to_str(self.redis_client.getdel(key))

    def get_range(self, key, beg, end):
        """
        Returns the substring of the string value stored at key provided. Inputs start and end value (both inclusive)
        Parameters:
            key: redis key
            beg (int): start offset value (inclusive)
            end (int): end offset value (inclusive)
        Returns:
            string: response
        Examples:
            str_redis = redis_client("string")
            str_redis.set("name", "dummy response")

            str_redis.get_range("name", 6, 8) --> "res"
        """
        if self.check_valid_key(key) and not self.exists(key):
            err_msg = "RedisString: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        return decode_byte_to_str(self.redis_client.getrange(key, beg, end)) if check_val_type(beg, int) and \
            check_val_type(end, int) else None

    def set_range(self, key, offset, value):
        """
        Method to overwrite bytes in the value of name starting at offset with value. Returns the new string value
        If offset plus the length of value exceeds the length of the original value, the new value will be larger
        than before. If offset exceeds the length of the original value, ``null`` bytes will be used to pad between the
        end of the previous value and the start of what’s being injected.
        Parameters:
            key: redis key
            offset (int): offset value
            value (str): string value to overwrite
        Returns:
            boolean: new value
        Examples:
            str_redis = redis_client("string")
            str_redis.set("name", "dummy")

            str_redis.set_range("name", 8, "response") --> True

            str_redis.get("name") --> "dummy\x00\x00\x00response"
        """
        return self.redis_client.setrange(key, offset, value) > 0 if self.check_valid_key(key) and is_valid(value) and \
            check_val_type(offset, int) else None

    def get_length(self, key):
        """
        Method to get length of value corresponding to given key.
        Parameters:
            key: redis key
        Returns:
            int: length
        Examples:
            str_redis = redis_client("string")
            redis_client("string").set("name", "dummy")

            str_redis.get_length("name") --> 5
        """
        if self.check_valid_key(key) and not self.exists(key):
            err_msg = "RedisString: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return 0

        return len(self.get(key))

    def increment_by(self, key, increment=1):
        """
        Method to increment the value of key by ``increment`` value. If no key exists, the value will be initialized
        as ``increment`` value
        Parameters:
            key: redis key
            increment (int): increment amount (default: 1)
        Returns:
            int: new value
        Examples:
            str_redis = redis_client("string")
            str_redis.set("counter", "1")

            type 1: str_redis.increment_by("counter") --> 1

            type 2: str_redis.increment_by("counter", 5) --> 6
        """
        if not (self.check_valid_key(key) and check_val_type(increment, int)):
            return None
        if self.exists(key) and not is_int_value(self.get(key)):
            err_msg = "RedisString: Value Error. Value is not an integer or out of range."
            logging.exception(err_msg)
            return None
        return self.redis_client.incrby(key, increment)

    def decrement_by(self, key, decrement=1):
        """
        Method to decrement the value of key by ``decrement`` value. If no key exists, the value will be initialized
        as ``decrement`` value
        Parameters:
            key: redis key
            decrement (int): increment amount (default: 1)
        Returns:
            int: new value
        Examples:
            str_redis = redis_client("string")
            str_redis.set("counter", "10")

            type 1: str_redis.decrement_by("counter") --> 9

            type 2: str_redis.decrement_by("counter", 5) --> 5
        """
        if not (self.check_valid_key(key) and check_val_type(decrement, int)):
            return None
        if self.exists(key) and not is_int_value(self.get(key)):
            err_msg = "RedisString: Value Error. Value is not an integer or out of range."
            logging.exception(err_msg)
            return None
        return self.redis_client.decrby(key, decrement)
