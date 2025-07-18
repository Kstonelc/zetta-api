from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    name = Column(String, nullable=False, unique=True)
    api_key = Column(String, nullable=True)  # API KEY
    desc = Column(Text)

    # 双向绑定 级联删除
    models = relationship(
        "Model", back_populates="provider", cascade="all, delete-orphan"
    )

    # 虚拟属性
    @property
    def get_types(self) -> list[str]:
        type_set = set()
        for model in self.models:
            if model.types:
                type_set.update(model.types)
        return list(type_set)

    # 导出虚拟属性字段
    def to_dict(self):
        data = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        data["types"] = self.get_types

        for rel in self.__mapper__.relationships:
            value = getattr(self, rel.key)
            if value is None:
                data[rel.key] = None
            elif isinstance(value, list):
                data[rel.key] = [vars(v).copy() for v in value]
            else:
                data[rel.key] = vars(value).copy()

        return data
