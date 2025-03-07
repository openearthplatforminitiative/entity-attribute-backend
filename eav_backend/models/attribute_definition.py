import uuid
from typing import Optional, List

from sqlalchemy import UUID, String, Enum, BOOLEAN
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from eav_backend.database import Base
from eav_backend.models.attribute_type import AttributeType


class AttributeDefinition(Base):
    __tablename__ = "attribute_definition"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the attribute definition.",
    )

    name: Mapped[str] = mapped_column(
        String, nullable=False, doc="The name of the attribute."
    )

    type: Mapped[AttributeType] = mapped_column(
        Enum(AttributeType, name="attribute_type_def"),
        nullable=False,
        doc="The type of the attribute, e.g., STRING, INTEGER, ENUM, etc.",
    )

    include_in_summary: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        doc="Whether this attribute should be returned in a summary response.",
    )

    allowed_values: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
        doc="Optional list of allowed values if the attribute type is ENUM.",
    )

    def __repr__(self) -> str:
        return f"<AttributeDefinition(id={self.id}, name={self.name}, type={self.type}, allowed_values={self.allowed_values})>"
