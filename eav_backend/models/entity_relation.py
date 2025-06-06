import uuid

from sqlalchemy import String, ForeignKey, and_
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eav_backend.database import Base


class EntityRelation(Base):
    __tablename__ = "entity_relation"

    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entity.id"),
        primary_key=True,
        doc="ID of the source entity.",
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("entity.id"),
        primary_key=True,
        doc="ID of the target (related) entity.",
    )

    collection_name: Mapped[str] = mapped_column(
        String, nullable=False, doc="Collection name for the related entity."
    )

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        doc="Flag indicating whether the entity is deleted.",
    )

    # Relationship to the target entity.
    target_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=lambda: [EntityRelation.target_entity_id],
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<EntityRelation(source={self.source_entity_id}, "
            f"target={self.target_entity_id}, "
            f"collection_name={self.collection_name})>"
        )
