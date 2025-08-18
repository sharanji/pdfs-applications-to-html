import logging

from redis.exceptions import ConnectionError as RedisConnectionError
from .redis_exceptions import RedisDataTypeError, RedisResponseError

from plutus_libs.external_vendors.redis.redis import RedisSyncClient
from app_redis.constants import redis_config

def setup_redis_client():
    """
    Method to set up a redis client connection
    Returns:
        RedisConnection: redis_client
    """
    redis_client = None
    try:
        redis_client = RedisSyncClient(redis_config).get_client()
    except RedisConnectionError as exc:
        logging.exception("Error in connecting to redis. Exception {}".format(exc))

    return redis_client


def is_valid(key):
    """
    Method to validate a general key data type. Throws RedisDataTypeError error when key type is invalid
    Parameters:
        key: redis key name
    Returns:
        boolean: True
    """
    if not isinstance(key, (int, float, str, bytes)):
        err = "Invalid input of key type: '%s'. Convert to a bytes, string, int or float first." % type(key).__name__
        logging.exception(err)
        raise RedisDataTypeError(err)
    return True


def is_valid_key_type(expected, actual):
    """
    Method to validate redis value type stored into db. Throws RedisResponseError when data type mismatches.
    Also, bypasses key doesn't exist i.e. actual value is 'none'
    Parameters:
        expected: expected value type
        actual: actual value type
    Returns:
        boolean: True
    """
    if actual == "none":
        return True
    if expected != actual:
        err_msg = "Wrong Type Operation. Excepted '%s' value but received '%s' value" % (expected, actual)
        logging.exception(err_msg)
        raise RedisResponseError(err_msg)
    return True


def is_valid_value_type(expected, actual):
    """
    Method to validate redis value data type before set/update. Throws RedisResponseError when data type mismatches
    Parameters:
        expected: expected value type
        actual: actual value type
    Returns:
        boolean: True
    """
    if expected == "string" and isinstance(actual, str):
        return True
    if expected == "list" and isinstance(actual, list):
        return True
    if expected == "set" and isinstance(actual, set):
        return True
    if expected == "hash" and isinstance(actual, dict):
        return True

    err_msg = "Wrong Type Operation. Excepted '%s' value but received '%s' value" % (expected, type(actual).__name__)
    logging.exception(err_msg)
    raise RedisResponseError(err_msg)


def is_int_value(value):
    """
    Method to check string value is int. Throws ValueError if it cannot be converted to int
    Parameters:
        value (str): string value
    Returns:
        boolean: response
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def decode_byte_to_str(value):
    """
    Method to convert byte value to string value. Return the decoded binary string, or a string, depending on type
    Parameters:
        value (byte): byte value
    Returns:
        str: string value
    """
    try:
        result = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
        if result == "null":
            return None
        return result
    except AttributeError as exc:
        logging.exception(msg=str(exc))


def list_decode_byte_to_str(arr):
    """
    Method to convert list of byte-values to list of str-values
    Parameters:
        arr (list): list of byte values
    Returns:
        list: list of str values
    """
    if arr is None:
        return arr
    return [decode_byte_to_str(value) for value in arr]


def set_decode_byte_to_str(_set):
    """
    Method to convert set of byte-values to set of str-values
    Parameters:
        _set: (set): set of byte values
    Returns:
        set: set of str values
    """
    return {decode_byte_to_str(value) for value in _set}


def hash_decode_byte_to_str(_dict):
    """
        Method to convert dict of byte-values to dict of str-values
        Parameters:
            _dict: (dict): key-value pair map of byte values
        Returns:
            dict: key-value pair map of str values
    """
    return {decode_byte_to_str(key): decode_byte_to_str(val) for key, val in _dict.items()}


def check_val_type(value, instance):
    """
        Method to evaluate instance type of given 'value'. Throws RedisResponseError when instance type does not
        match.
        Parameters:
           value: field value
           instance: expected instance
        Returns:
            boolean: response
    """
    if not isinstance(value, instance):
        err_msg = "Value Type Error. Expected '%s' but value type found '%s'" % \
                  (type(instance).__name__, type(value).__name__)
        logging.info(err_msg)
        raise RedisResponseError(err_msg)
    return True
