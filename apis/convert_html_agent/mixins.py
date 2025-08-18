from sqlalchemy.inspection import inspect

class SerializerMixin:
    def to_dict(self, include_relationships=False):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        if include_relationships:
            for name, relation in inspect(self.__class__).relationships.items():
                value = getattr(self, name)
                if value is None:
                    data[name] = None
                elif relation.uselist:
                    data[name] = [item.to_dict() for item in value]
                else:
                    data[name] = value.to_dict()
        return data
