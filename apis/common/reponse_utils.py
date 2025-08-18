import json
import time
from flask import Response


def event_stream_wrapper(func):
    def wrapper(*args, **kwargs):
        def generate():
            for data in func(*args, **kwargs):
                yield f"data: {json.dumps(data)}\n\n"  # SSE format
        return Response(generate(), mimetype="text/event-stream")
    return wrapper

def response_wrap(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return Response(wrapper, mimetype='application/json')