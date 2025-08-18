from db import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.inspection import inspect
from .mixins import SerializerMixin

class ConvertedTemplates(Base, SerializerMixin):
    __tablename__ = 'Templates'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(100), nullable=False, unique=True)
    created_by = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sections = relationship("TemplateSections", back_populates="template", cascade="all, delete-orphan")

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



class TemplateSections(Base, SerializerMixin):
    __tablename__ = 'Template_Sections'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey('Templates.id', ondelete="CASCADE"), nullable=False)
    section_name = Column(String(255), nullable=False)
    section_content = Column(Text, nullable=True)
    order = Column(Integer, nullable=True)

    template = relationship("ConvertedTemplates", back_populates="sections")

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