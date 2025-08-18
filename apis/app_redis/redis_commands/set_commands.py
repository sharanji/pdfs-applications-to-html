import logging

from app_redis.pickle_helper import Pickle_Helper
from app_redis.redis_exceptions import RedisKeyError

from .base_commands import RedisBase


class RedisSet(RedisBase):
    """
    Redis Set Commands
    """

    def __init__(self, redis_client):
        super(RedisSet, self).__init__(redis_client)
        self.type = "set"

    def get(self, key):
        """
        Method to get the all members of set for ``key``
        Parameters:
            key: redis key
        Returns:
            set: response
        Examples:
            redis_set = redis_client("set")

            redis_set.get("alpha") --> {"a", "b", "c"}
        """
        if not self.exists(key):
            err_msg = "RedisSet: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return {}
        return Pickle_Helper.deserialize_set(self.redis_client.smembers(key))

    def set(self, key, value, secs=None, millisecs=None):
        """
        Method to set key and set of values into db. Returns True when successfully set
        Parameters:
            key: redis key
            value: redis set value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            redis_set = redis_client("set")

            type 1: redis_set.set("alpha", {"a", "b", "c"}) --> True

            type 2: redis_set.set("alpha", {"a", "b", "c"}, secs=120)  --> True

            type 3: redis_set.set("alpha", {"a", "b", "c"}, millisecs=4000)  --> True
        """
        value = Pickle_Helper.serialize_set(value)
        response_set = self.redis_client.sadd(key, *value) > 0
        return self.set_expire(key, secs, millisecs) and response_set

    def update(self, key, value, secs=None, millisecs=None):
        """
        Method to update key set of values. Returns True when successfully updated
        Parameters:
            key: redis key
            value: redis value
            secs (optional): set expiry flag in seconds
            millisecs (optional): set expiry flag in milliseconds
        Returns:
            boolean: response
        Examples:
            redis_set = redis_client("set")

            type 1: redis_set.update("alpha", {"a", "b", "c"})

            type 2: redis_set.update("alpha", {"a", "b", "c"}, secs=120)  --> True

            type 3: redis_set.update("alpha", {"a", "b", "c"}, millisecs=4000)  --> True
        """
        key = Pickle_Helper.serialize_value(key)
        value = Pickle_Helper.serialize_set(value)
        if not self.exists(key):
            err_msg = "RedisSet: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        self.delete(key)
        update_response = self.redis_client.sadd(key, *value) > 0
        return self.set_expire(key, secs, millisecs) and update_response

    def get_length(self, key):
        """
        Method to return the length of set
        Parameters:
            key: redis key
        Returns:
            int: length
        Examples:
            redis_set = redis_client("set")

            redis_set.set("alpha", {"a", "b", "c"})

            redis_set.get_length("alpha") --> 3
        """
        if not self.exists(key):
            err_msg = "RedisSet: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return 0
        return self.redis_client.scard(key)

    def add_values(self, key, *values):
        """
        Method to add key and set of values into db. Returns True when successfully added
        Parameters:
            key: redis key
            values: redis value
        Returns:
            boolean: response
        Examples:
            redis_set = redis_client("set")
            redis_set.set("alpha", {"a", "b", "c"})

            type 1: redis_set.add_values("alpha", "d")

            type 2: redis_set.add_values("alpha", "d", "e")

            type 3: redis_set.add_values("alpha", *["d", "e"])
        """
        values = Pickle_Helper.serialize_set(*values)
        return self.redis_client.sadd(key, *values) > 0

    def diff(self, keys, *args):
        """
        Method to return the difference of sets specified by ``keys``
        Parameters:
            keys (list): keys of set
            args (list): keys of set
        Returns:
            set: result set
        Examples:
            key1 = {"a", "b", "c", "d"}
            key2 = {"c"}
            key3 = {"a", "c", "e"}

            redis_set = redis_client("set")
            redis_set.set("key1", key1)
            redis_set.set("key2", key2)
            redis_set.set("key3", key3)

            redis_set.diff("key1", "key2", "key3")  -->  {"b", "d"}
        """
        return Pickle_Helper.deserialize_set(self.redis_client.sdiff(keys, *args))

    def diff_store(self, destination, keys, *args):
        """
        Method to return the difference of sets specified by ``keys`` stored in set named ``destination``
        Parameters:
            destination (str): destination set key name
            keys (list): keys of set
            args (list): keys of set
        Returns:
            boolean: response
        Examples:
            key1 = {"a", "b", "c", "d"}
            key2 = {"c"}
            key3 = {"a", "c", "e"}

            redis_set = redis_client("set")
            redis_set.set("key1", key1)
            redis_set.set("key2", key2)
            redis_set.set("key3", key3)

            redis_set.diff_store("key", "key1", "key2", "key3")  -->  True

            redis_set.get("key")  -->  -->  {"b", "d"}
        """
        return self.redis_client.sdiffstore(destination, keys, *args) > 0

    def intersect(self, keys, *args):
        """
        Method to return the intersection of sets specified by ``keys``
        Parameters:
            keys (list): keys of set
            args (list): keys of set
        Returns:
            set: result set
        Examples:
            key1 = {"a", "b", "c", "d"}
            key2 = {"c"}
            key3 = {"a", "c", "e"}

            redis_set = redis_client("set")
            redis_set.set("key1", key1)
            redis_set.set("key2", key2)
            redis_set.set("key3", key3)

            redis_set.intersect("key1", "key2", "key3")  -->  {"c"}
        """
        return Pickle_Helper.deserialize_set(self.redis_client.sinter(keys, *args))

    def intersect_store(self, destination, keys, *args):
        """
        Method to return the intersection of sets specified by ``keys`` stored in set named ``destination``
        Parameters:
            destination (str): destination set key name
            keys (list): keys of set
            args (list): keys of set
        Returns:
            boolean: response
        Examples:
            key1 = {"a", "b", "c", "d"}
            key2 = {"c"}
            key3 = {"a", "c", "e"}

            redis_set = redis_client("set")
            redis_set.set("key1", key1)
            redis_set.set("key2", key2)
            redis_set.set("key3", key3)
            redis_set.intersect_store("key", "key1", "key2", "key3")  -->  True

            redis_set.get("key") --> {"c"}
        """
        return self.check_valid_key(destination) and self.redis_client.sinterstore(destination, keys, *args) > 0

    def union(self, keys, *args):
        """
        Method to return the union of sets specified by ``keys``
        Parameters:
            keys (list): keys of set
            args (list): keys of set
        Returns:
            set: result set
        Examples:
            key1 = {"a", "b", "c", "d"}
            key2 = {"c"}
            key3 = {"a", "c", "e"}

            redis_set = redis_client("set")
            redis_set.set("key1", key1)
            redis_set.set("key2", key2)
            redis_set.set("key3", key3)

            redis_set.union("key1", "key2", "key3")  -->  {"a", "b", "c", "d", "e"}
        """
        return Pickle_Helper.deserialize_set(self.redis_client.sunion(keys, *args))

    def union_store(self, destination, keys, *args):
        """
        Method to return the union of sets specified by ``keys`` stored in set named ``destination``
        Parameters:
            destination (str): destination set key name
            keys (list): keys of set
            args (list): keys of set
        Returns:
            boolean: response
        Examples:
            key1 = {"a", "b", "c", "d"}
            key2 = {"c"}
            key3 = {"a", "c", "e"}

            redis_set = redis_client("set")
            redis_set.set("key1", key1)
            redis_set.set("key2", key2)
            redis_set.set("key3", key3)
            redis_set.union_store("key", "key1", "key2", "key3")  -->  True

            redis_set.get("key") --> {"a", "b", "c", "d", "e"}
        """
        return self.redis_client.sunionstore(destination, keys, *args) > 0

    def ismember(self, key, element):
        """
        Method to return a boolean indicating if ``element`` is a member of set ``key``
        Parameters:
            key: redis key
            element: value to be checked
        Returns:
            boolean: response
        Examples:
            redis_set = redis_client("set")

            redis_set.set("alpha", {"a", "b", "c"})

            redis_set.ismember("alpha", "b") --> True
        """
        element = Pickle_Helper.serialize_value(element)
        if not self.exists(key):
            err_msg = "RedisSet: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        return self.redis_client.sismember(key, element)

    def remove_values(self, key, *values):
        """
        Method to remove ``values`` from set ``key``
        Parameters:
            key: redis key
            values: values to be removed
        Returns:
            boolean: response
        Examples:
            redis_set = redis_client("set")
            redis_set.set("alpha", {"a", "b", "c"})

            type 1: redis_set.remove_values("alpha", "b") --> True

            type 2: redis_set.remove_values("alpha", *["b", "c"]) --> True
        """
        if not self.exists(key):
            err_msg = "RedisSet: Key Not Found. Provided key does not exists in cache."
            logging.info(err_msg)
            return False
        values = Pickle_Helper.serialize_list(*values)
        return self.redis_client.srem(key, *values) > 0
