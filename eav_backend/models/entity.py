import uuid
from typing import List, Optional

from sqlalchemy import UUID, String, ForeignKey, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eav_backend.database import Base
from eav_backend.models.entity_relation import EntityRelation


class Entity(Base):
    __tablename__ = "entity"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the entity.",
    )

    entity_type: Mapped[str] = mapped_column(
        String, nullable=False, doc="The type of the entity."
    )

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        doc="Flag indicating whether the entity is deleted.",
    )

    attributes: Mapped[List["Attribute"]] = relationship(
        "Attribute", back_populates="entity", cascade="all, delete-orphan"
    )

    relations: Mapped[List[EntityRelation]] = relationship(
        "EntityRelation",
        primaryjoin="and_(Entity.id == EntityRelation.source_entity_id, EntityRelation.is_deleted == False)",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def is_of_type(self, immediate_parent_type) -> bool:
        return self.entity_type.lower() == immediate_parent_type.lower()
