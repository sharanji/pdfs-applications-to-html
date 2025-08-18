def response_format(inner_func):
    def warp():
        return {
            "message":"success",
            "response" : inner_func()
        }
    return warp
