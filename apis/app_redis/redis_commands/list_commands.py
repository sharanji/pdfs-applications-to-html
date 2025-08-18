import logging

from app_redis.pickle_helper import Pickle_Helper
from app_redis.redis_exceptions import RedisKeyError, RedisResponseError
from app_redis.utils import is_valid, check_val_type

from .base_commands import RedisBase


class RedisList(RedisBase):
    """
    Redis List Commands
    """

    def __init__(self, redis_client):
        super(RedisList, self).__init__(redis_client)
        self.type = "list"

    def list_range(self, key, start, stop):
        """
        Method to return a slice of the list ``key`` between position ``start`` and ``end`` (can be negative numbers)
        Parameters:
            key: redis key
            start (int): start offset
            stop (int): stop offset
        Returns:
            list: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow", "green"])

            list_redis.list_range("colors", 1, 3) --> ["blue, "yellow"]
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return []

        try:
            return Pickle_Helper.deserialize_list(self.redis_client.lrange(key, start, stop))
        except Exception as e:
            err_msg = f"RedisList Range: {e}."
            logging.exception(err_msg)
        return []

    def get(self, key):
        """
        Method to return complete list
        Parameters:
            key: redis key
        Returns:
            list: response
        Examples:
            list_redis = redis_client("list")

            list_redis.get("colors") --> ["red", "blue", "yellow", "green"]
        """
        return Pickle_Helper.deserialize_list(self.list_range(key, 0, -1))

    def set(self, key, value: list, secs=None, millisecs=None):
        """
        Method to set key and list of values into db. Returns True when successfully set
        Parameters:
            key: redis key
            value: redis value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")

            type 1: list_redis.set("colors", ["red", "blue", "yellow", "green"])  --> True

            type 2: list_redis.set("colors", ["red", "blue", "yellow", "green"], secs=120)  --> True

            type 3: list_redis.set("colors", ["red", "blue", "yellow", "green"], millisecs=4000)  --> True
        """
        value = Pickle_Helper.serialize_list(value)
        set_response = self.redis_client.rpush(key, *value) > 0
        return self.set_expire(key, secs, millisecs) and set_response

    def update(self, key, value, secs=None, millisecs=None):
        """
        Method to update key and list of values. Returns True when successfully updated
        Parameters:
            key: redis key
            value: redis value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")

            type 1. list_redis.set("colors", ["red", "blue"])  --> True

            type 2. list_redis.set("colors", ["red", "blue"], secs=120)  --> True

            type 3. list_redis.set("colors", ["red", "blue"], millisecs=4000)  --> True
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        value = Pickle_Helper.serialize_list(value)
        self.delete(key)
        response_update = self.redis_client.rpush(key, *value) > 0
        return self.set_expire(key, secs, millisecs) and response_update

    def get_element(self, key, index):
        """
        Method to return the item from list by ``key`` at position ``index``. Returns the value
        Parameters:
            key: redis key
            index (int): index position
        Returns:
            str: response
        Examples:
            list_redis = redis_client("list")

            list_redis.set("colors", ["red", "blue", "yellow", "green"])

            list_redis.get_element("colors", 1) --> "blue"
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        value = check_val_type(
            index, int) and self.redis_client.lindex(key, index)
        if not value:
            err_msg = "List Index Error. Index key is out of range"
            logging.exception(err_msg)
            return None
        return Pickle_Helper.deserialize_value(value)

    def insert_before(self, key, pivot, element):
        """
        Method to insert ``element`` into list immediately BEFORE ``pivot`` element.
        Parameters:
            key: redis key
            pivot: pivot element
            element: value to be inserted
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow"])

            list_redis.insert_before("colors", "blue", "orange") --> True

            list_redis.get("colors") --> ["red", "orange", "blue", "yellow"]
        """
        response = False
        pivot = Pickle_Helper.serialize_value(pivot)
        element = Pickle_Helper.serialize_value(element)
        if is_valid(element) and is_valid(pivot):
            response = self.redis_client.linsert(
                key, "BEFORE", pivot, element) > -1
        if not response:
            err_msg = "'Pivot' Element Not Found in list"
            logging.exception(err_msg)
        return response

    def insert_after(self, key, pivot, element):
        """
        Method to insert ``element`` into list immediately AFTER ``pivot`` element.
        Parameters:
            key: redis key
            pivot: pivot element
            element: value to be inserted
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow"])

            list_redis.insert_after("colors", "blue", "orange") --> True

            list_redis.get("colors") --> ["red", "blue", "orange", "yellow"]
        """
        response = False
        pivot = Pickle_Helper.serialize_value(pivot)
        element = Pickle_Helper.serialize_value(element)
        if is_valid(element) and is_valid(pivot):
            response = self.redis_client.linsert(
                key, "AFTER", pivot, element) > -1
        if not response:
            err_msg = "'Pivot' Element Not Found in list"
            logging.exception(err_msg)
        return response

    def get_length(self, key):
        """
        Method to return the length of list
        Parameters:
            key: redis key
        Returns:
            int: length
        Examples:
            list_redis = redis_client("list")

            list_redis.set("colors", ["red", "blue", "yellow"])

            list_redis.get_length("colors") --> 3
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return 0
        return self.redis_client.llen(key)

    def left_push(self, key, *values):
        """
        Method to push ``values`` onto the head of the list corresponding to ``key``
        Parameters:
            key: redis key
            values: redis values. can be int, float, bytes, str or list
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow"])

            type 1. list_redis.left_push("colors", "purple")  # single value

            type 2. list_redis.left_push("colors", "purple", "orange") # values args

            type 3. list_redis.left_push("colors", *["purple", "orange"]) # list of values
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        values = Pickle_Helper.serialize_list(list(values))
        return self.redis_client.lpush(key, *values) > 0

    def right_push(self, key, *values):
        """
        Method to push ``values`` onto the tail of the list corresponding to ``key``
        Parameters:
            key: redis key
            values: redis values. can be int, float, bytes, str or list
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow"])

            type 1. list_redis.right_push("colors", "purple")  # single value

            type 2. list_redis.right_push("colors", "purple", "orange") # values args

            type 3. list_redis.right_push("colors", *["purple", "orange"]) # list of values
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        values = Pickle_Helper.serialize_list(list(values))
        return self.redis_client.rpush(key, *values) > 0

    def left_pop(self, key, count=1):
        """
        Method to pop values from the head of the list corresponding to ``key``
        Parameters:
            key: redis key
            count: no of values to pop (default: 1)
        Returns:
            str(or list): response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow"])

            type 1: list_redis.left_pop("colors")  -->  "red"

            type 2: list_redis.left_pop("colors", count=2)  -->  ["blue", "red"]
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        if check_val_type(count, int) and count < 0:
            err_msg = "RedisList: Value Error. Value must be positive."
            logging.exception(err_msg)
            return None
        value = self.redis_client.lpop(
            key) if count == 1 else self.redis_client.lpop(key, count)
        if not value:
            err_msg = "RedisList: Value Not Found. List is empty."
            logging.exception(err_msg)
            return None
        return Pickle_Helper.deserialize_value(value)

    def right_pop(self, key, count=1):
        """
        Method to pop values from the tail of the list corresponding to ``key``
        Parameters:
            key: redis key
            count: no of values to pop (default: 1)
        Returns:
            str(or list): response
        Examples:
            list_redis = redis_client("list")
            redis_client("list").set("colors", ["red", "blue", "yellow"])

            type 1: list_redis.left_pop("colors")  -->  "yellow"

            type 2: list_redis.left_pop("colors", count=2)  -->  ["blue", "yellow"]
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        if check_val_type(count, int) and count < 0:
            err_msg = "RedisList: Value Error. Value must be positive."
            logging.exception(err_msg)
            return None
        value = self.redis_client.rpop(
            key) if count == 1 else self.redis_client.rpop(key, count)
        if not value:
            err_msg = "RedisList: Value Not Found. List is empty."
            logging.exception(err_msg)
            return None
        return Pickle_Helper.deserialize_value(value)

    def set_element(self, key, index, value):
        """
        Method to set element at ``index`` of list ``key`` to ``value``
        Parameters:
            key: redis key
            index (int): index of list
            value: new value
        Returns:
            boolean: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow"])

            list_redis.set_element("colors", 2, "purple") --> True

            list_redis.get("colors")  -->  ["red", "blue", "purple"]
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        if check_val_type(index, int) and not self.redis_client.lindex(key, index):
            err_msg = "RedisList: List Index Error. Index key is out of range."
            logging.exception(err_msg)
            return False
        value = Pickle_Helper.serialize_value(value)
        return self.redis_client.lset(key, index, value)

    def trim(self, key, start, stop):
        """
        Method to trim the list ``key``, removing all values not within the slice between ``start`` and ``end``.
        start and end can be negatives
        Parameters:
            key: redis key
            start (int): start offset
            stop (int): stop offset
        Returns:
             boolean: response
        Examples:
            list_redis = redis_client("list")
            list_redis.set("colors", ["red", "blue", "yellow", "green"])

            list_redis.trim("colors", 1, 2)  -->  True

            list_redis.get("colors")  -->  ["blue", "yellow"]
        """
        if not self.exists(key):
            err_msg = "RedisList: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return None
        try:
            return self.redis_client.ltrim(key, start, stop) if check_val_type(start, int) \
                and check_val_type(stop, int) else False
        except Exception as e:
            logging.exception(e)
            return None
