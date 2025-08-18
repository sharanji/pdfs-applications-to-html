from redis.exceptions import RedisError


class RedisBaseException(RedisError):

    def __init__(self, message, error=None):
        self.message = message
        self.error = error

        super(RedisBaseException, self).__init__(message)


class RedisKeyError(RedisBaseException):

    def __init__(self, message, error=None):
        self.error = "RedisKeyError"

        super(RedisKeyError, self).__init__(message, error=error)


class RedisDataTypeError(RedisBaseException):
    # Data error
    def __init__(self, message, error=None):
        self.error = "RedisDataTypeError"

        super(RedisDataTypeError, self).__init__(message, error=error)


class RedisResponseError(RedisBaseException):
    # Response error
    def __init__(self, message, error=None):
        self.error = "RedisResponseError"

        super(RedisResponseError, self).__init__(message, error=error)


class RedisSyntaxError(RedisBaseException):

    def __init__(self, message, error=None):
        self.error = "RedisSyntaxError"

        super(RedisSyntaxError, self).__init__(message, error=error)
