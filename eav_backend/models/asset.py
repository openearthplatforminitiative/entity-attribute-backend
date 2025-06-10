import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from eav_backend.config import settings
from eav_backend.database import Base
from eav_backend.models.asset_content import AssetContent


class Asset(Base):
    __tablename__ = "asset"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the asset.",
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="The name of the file asset.",
    )

    mimetype: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="The MIME type of the file (e.g., application/pdf, image/png).",
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="The size of the file in bytes.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        doc="The timestamp when the asset was created.",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        doc="The timestamp when the asset was last updated.",
    )

    checksum: Mapped[str] = mapped_column(
        String,
        nullable=True,
        doc="A checksum to verify the integrity of the file.",
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entity.id"),
        nullable=False,
        doc="Reference to the entity that this asset belongs to.",
    )

    content: Mapped[AssetContent] = relationship(
        "AssetContent",
        uselist=False,
        back_populates="asset",
        lazy="select",
    )

    @hybrid_property
    def is_valid(self) -> bool:
        """Check if the asset has a valid checksum."""
        return self.checksum is not None

    @hybrid_property
    def url(self) -> str:
        return settings.asset_content_url(self.id)
