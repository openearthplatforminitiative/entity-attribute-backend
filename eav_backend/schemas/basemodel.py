import abc

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel, abc.ABC):
    class Config:
        from_attributes = True
        populate_by_name = True
