import logging

from app_redis.utils import is_valid, is_valid_key_type, is_valid_value_type
from app_redis.redis_exceptions import RedisSyntaxError


class RedisBase():
    """
    Redis Base Commands
    """

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.type = None

    def get(self, key):
        """
        get method base class
        Parameters:
            key: redis key
        Returns:
            value: response
        """

    def set(self, key, value, secs=None, millisecs=None):

        """
        set method base class
        Parameters:
            key: redis key
            value: redis value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        """

    def exists(self, key):
        """
        Method to check if key exists
        Parameters:
            key: redis key
        Returns:
            boolean: response
        Examples:
            str_redis = redis_client("string")

            str_redis.exists("name") --> True
        """
        return bool(self.redis_client.exists(key))

    def delete(self, key):
        """
        Method to delete key. If key does not exist then return False else True when successfully deleted
        Parameters:
            key: redis key
        Returns:
            boolean: response
        Examples:
            str_redis = redis_client("string")

            str_redis.delete("name") --> True
        """
        return is_valid(key) and bool(self.redis_client.delete(key))

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
        """

    def get_length(self, key):
        """
        Method to get length of value / no of items corresponding to given key.
        Parameters:
            key: redis key
        Returns:
            int: length
        """

    def get_type(self, key):
        """
        Method to get data-type of ``key``. if ``key`` does not exist it returns ``none``
        Parameters:
            key: redis key
        Returns:
            str: response
        """
        return self.redis_client.type(key) if is_valid(key) else None

    def set_expire(self, key, secs=None, millisecs=None):
        """
        Method to set expiry flag in milliseconds
        Parameters:
            key: redis key
            secs: set expiry flag in seconds
            millisecs: set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            redis_list = redis_client("list")

            type1: redis_list.set_expire("dummy", secs=120) --> True

            type2: redis_list.set_expire("dummy", millisecs=400) --> True
        """
        if secs and millisecs:
            err_msg = "Syntax Error. Set expire time either in seconds or milliseconds."
            logging.exception(err_msg)
            return False
        if secs:
            return self.redis_client.expire(key, secs)
        if millisecs:
            return self.redis_client.pexpire(key, millisecs)
        # if both secs and millisecs value None then automatically return true
        return True

    def check_valid_key(self, key):
        """
            Method to check if key is valid
            Parameters:
                key: redis key
            Returns:
                boolean: response
        """
        return is_valid(key)

    def check_valid_key_value(self, key, value):
        """
            Method to check if key and value are valid
            Parameters:
                key: redis key
                value: redis value
            Returns:
                boolean: response
        """
        return is_valid(key) and is_valid_value_type(expected=self.type, actual=value)
