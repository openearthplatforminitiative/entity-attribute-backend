import uuid

from sqlalchemy import String, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eav_backend.database import Base


class EntityRelationDefinition(Base):
    __tablename__ = "entity_relation_definition"

    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entity_definition.id"),
        primary_key=True,
        doc="ID of the source entity.",
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entity_definition.id"),
        primary_key=True,
        doc="ID of the target (related) entity.",
    )
    collection_name: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        nullable=False,
        doc="Collection name for the related entity.",
    )

    api_endpoints: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=True,
        doc="List of API endpoints this entity should have.",
    )

    target_entity: Mapped["EntityDefinition"] = relationship(
        "EntityDefinition",
        foreign_keys=lambda: [EntityRelationDefinition.target_entity_id],
    )

    def __repr__(self) -> str:
        return (
            f"<EntityRelation(source={self.source_entity_id}, "
            f"target={self.target_entity_id}, "
            f"collection_name={self.collection_name})>"
        )
