from __future__ import annotations

import uuid

from pydantic import Field

from eav_backend.schemas.basemodel import BaseModel


class EntityRelationRequest(BaseModel):
    entity: str = Field(description="The name of the related entity.")
    collection_name: str = Field(
        description="The name of the collection of the related entity."
    )
    api_endpoints: list[str] = Field(
        alias="apiEndpoints",
        description="List of api endpoints this entity relation should have.",
        default=False,
    )


class EntityRelationResponse(BaseModel):
    id: uuid.UUID
    entity: str = Field(description="The name of the related entity.")
    collection_name: str = Field(
        description="The name of the collection of the related entity."
    )

    # @field_validator("related_entities", mode="before")
    # def convert_related_entities(cls, value):
    #     """
    #     If the incoming value is a list of SQLAlchemy objects (which have an 'id' attribute),
    #     convert them to a list of UUIDs.
    #     """
    #     if isinstance(value, list) and value:
    #         # Check if the first element has an 'id' attribute; assume all do.
    #         if hasattr(value[0], "name"):
    #             return [item.name for item in value]
    #     return value
