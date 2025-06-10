from __future__ import annotations

import uuid
from typing import List

from pydantic import Field, field_validator

from eav_backend.schemas.attribute_definition import (
    AttributeDefinitionResponse,
    AttributeDefinitionRequest,
)
from eav_backend.schemas.basemodel import BaseModel
from eav_backend.schemas.entity_relation import (
    EntityRelationRequest,
    EntityRelationResponse,
)


class EntityDefinitionRequest(BaseModel):
    name: str = Field(description="The name of the entity.")
    collection_name: str = Field(
        description="The name of the collection of these entities."
    )
    api_endpoints: list[str] = Field(
        alias="apiEndpoints",
        description="List of api endpoints this entity should have.",
        default=False,
    )
    return_summary_on_collection: bool = Field(
        alias="returnSummaryOnCollection",
        description="Whether this entity should return a summary object on the collection.",
        default=True,
    )
    supports_assets: bool = Field(
        alias="supportsAssets",
        description="Whether this entity supports to have assets/files linked to it.",
        default=False,
    )
    required_attributes: List[AttributeDefinitionRequest] = Field(
        alias="requiredAttributes",
        description="The required attributes for this entity.",
        default=[],
    )
    optional_attributes: List[AttributeDefinitionRequest] = Field(
        alias="optionalAttributes",
        description="The optional attributes for this entity.",
        default=[],
    )
    related_entities: List[EntityRelationRequest] = Field(
        alias="relatedEntities",
        description="The related entities for this entity.",
        default=[],
    )


class EntityDefinitionResponse(BaseModel):
    id: uuid.UUID
    name: str = Field(description="The name of the entity.")
    collection_name: str = Field(
        description="The name of the collection of these entities."
    )
    api_endpoints: list[str] = Field(
        alias="apiEndpoints",
        description="List of api endpoints this entity should have.",
        default=False,
    )

    return_summary_on_collection: bool = Field(
        alias="returnSummaryOnCollection",
        description="Whether this entity should return a summary object on the collection.",
        default=True,
    )

    supports_assets: bool = Field(
        alias="supportsAssets",
        description="Whether this entity supports to have assets/files linked to it.",
        default=False,
    )

    required_attributes: List[AttributeDefinitionResponse] = Field(
        alias="requiredAttributes",
        description="The required attributes for this entity.",
        default=[],
    )
    optional_attributes: List[AttributeDefinitionResponse] = Field(
        alias="optionalAttributes",
        description="The optional attributes for this entity.",
        default=[],
    )
    related_entities: List[EntityRelationResponse] = Field(
        alias="relatedEntities",
        description="The related entities for this entity.",
        default=[],
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
