import uuid
from typing import List

from sqlalchemy import (
    UUID,
    String,
    Table,
    Column,
    ForeignKey,
    BOOLEAN,
    INTEGER,
    BIGINT,
    ARRAY,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eav_backend.models.attribute_definition import AttributeDefinition
from eav_backend.database import Base
from eav_backend.models.endpoint_type import EndpointType
from eav_backend.models.entity_relation_definition import EntityRelationDefinition

# Join table for required attributes.
entity_required_attributes = Table(
    "entity_required_attributes",
    Base.metadata,
    Column(
        "entity_definition_id",
        PG_UUID(as_uuid=True),
        ForeignKey("entity_definition.id"),
        primary_key=True,
    ),
    Column(
        "attribute_definition_id",
        PG_UUID(as_uuid=True),
        ForeignKey("attribute_definition.id"),
        primary_key=True,
    ),
)

# Join table for optional attributes.
entity_optional_attributes = Table(
    "entity_optional_attributes",
    Base.metadata,
    Column(
        "entity_definition_id",
        PG_UUID(as_uuid=True),
        ForeignKey("entity_definition.id"),
        primary_key=True,
    ),
    Column(
        "attribute_definition_id",
        PG_UUID(as_uuid=True),
        ForeignKey("attribute_definition.id"),
        primary_key=True,
    ),
)


class EntityDefinition(Base):
    __tablename__ = "entity_definition"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the entity definition.",
    )

    name: Mapped[str] = mapped_column(
        String, nullable=False, doc="The name of the entity."
    )

    hash: Mapped[str] = mapped_column(
        String, nullable=False, doc="The hash of the entity."
    )

    collection_name: Mapped[str] = mapped_column(
        String, nullable=False, doc="The name of the collection of entities."
    )

    api_endpoints: Mapped[list[EndpointType]] = mapped_column(
        ARRAY(Enum(EndpointType, name="endpoint_type_def")),
        nullable=False,
        doc="List of API endpoints this entity should have.",
    )

    return_summary_on_collection: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        doc="Whether this entity should return a summary object on the collection.",
    )

    supports_assets: Mapped[bool] = mapped_column(
        BOOLEAN,
        nullable=False,
        doc="Whether this entity supports to have assets/files linked to it.",
    )

    required_attributes: Mapped[List[AttributeDefinition]] = relationship(
        "AttributeDefinition",
        secondary=entity_required_attributes,
    )

    optional_attributes: Mapped[List[AttributeDefinition]] = relationship(
        "AttributeDefinition", secondary=entity_optional_attributes
    )

    entity_relations: Mapped[List["EntityRelationDefinition"]] = relationship(
        "EntityRelationDefinition",
        primaryjoin=id == EntityRelationDefinition.source_entity_id,
        cascade="all, delete-orphan",
        lazy="joined",
    )

    @property
    def identifier(self) -> str:
        return self.name.lower()

    def should_have_endpoint(self, endpoint: str) -> bool:
        return endpoint in self.api_endpoints

    def __repr__(self) -> str:
        return f"<EntityDefinition(id={self.id}, name={self.name})>"
