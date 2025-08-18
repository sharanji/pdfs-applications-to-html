import uuid


def generate_request_id(request_id: str = None):
    return request_id if request_id else str(uuid.uuid4())
