import uuid
from typing import List, Optional

from pydantic import Field

from eav_backend.schemas.basemodel import BaseModel
from eav_backend.models.attribute_type import AttributeType


class AttributeDefinitionRequest(BaseModel):
    name: str
    type: AttributeType
    include_in_summary: Optional[bool] = Field(
        description="Whether this attribute should be included in the summary response.",
        alias="includeInSummary",
        default=False,
    )
    allowed_values: Optional[List[str]] = None


class AttributeDefinitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: AttributeType
    include_in_summary: Optional[bool] = Field(
        description="Whether this attribute should be included in the summary response.",
        alias="includeInSummary",
        default=False,
    )
    allowed_values: Optional[List[str]] = None
