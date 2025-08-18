import pickle
from app_redis.constants import PRIMITIVE_TYPES
from app_redis.utils import decode_byte_to_str


class Pickle_Helper:

    @staticmethod
    def serialize_value(field_value):
        if not isinstance(field_value, PRIMITIVE_TYPES):
            return pickle.dumps(field_value)
        return field_value

    @staticmethod
    def deserialize_value(field_value):
        if isinstance(field_value, bytes):
            try:
                return pickle.loads(field_value)
            except pickle.UnpicklingError as e:
                field_value = decode_byte_to_str(field_value)
        return field_value

    @staticmethod
    def serialize_dict(value: dict):
        serialized_dict = {}
        for key, value in value.items():
            key = Pickle_Helper.serialize_value(key)
            serialized_dict[key] = Pickle_Helper.serialize_value(value)
        return serialized_dict

    @staticmethod
    def deserialize_dict(value: dict):
        deserialized_dict = {}
        for key, value in value.items():
            key = Pickle_Helper.deserialize_value(key)
            deserialized_dict[key] = Pickle_Helper.deserialize_value(value)
        return deserialized_dict

    @staticmethod
    def serialize_list(values: list):
        return [Pickle_Helper.serialize_value(value) for value in values]

    @staticmethod
    def deserialize_list(values: list):
        return [Pickle_Helper.deserialize_value(value) for value in values]

    @staticmethod
    def serialize_set(values: set):
        return {Pickle_Helper.serialize_value(value) for value in values}

    @staticmethod
    def deserialize_set(values: set):
        return {Pickle_Helper.deserialize_value(value) for value in values}
