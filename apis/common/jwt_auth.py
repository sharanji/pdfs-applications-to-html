import time


def ReqAuth(original_function):
    def inner_function(*args, **kwargs):
        result = original_function(*args, **kwargs)
        return result

    return inner_function
