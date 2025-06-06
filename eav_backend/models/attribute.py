import uuid
from datetime import date
from typing import Optional

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape, from_shape
from pydantic_core import ValidationError
from shapely.geometry.geo import mapping, shape
from sqlalchemy import UUID, String, Integer, Float, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eav_backend.database import Base
from eav_backend.models import AttributeType


class Attribute(Base):
    __tablename__ = "attribute"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the attribute.",
    )

    name: Mapped[str] = mapped_column(
        String, nullable=False, doc="The name of the attribute."
    )

    type: Mapped[AttributeType] = mapped_column(
        Enum(AttributeType, name="attribute_type"),
        nullable=False,
        doc="The type of the attribute, e.g., STRING, INTEGER, ENUM, GEOMETRY, etc.",
    )

    # Type-specific columns for storing the attribute's value.
    value_str: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="String value of the attribute."
    )
    value_int: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, doc="Integer value of the attribute."
    )
    value_float: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, doc="Float value of the attribute."
    )
    value_boolean: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True, doc="Boolean value of the attribute."
    )
    value_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, doc="Date value of the attribute."
    )
    value_enum: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="Enum value of the attribute."
    )
    value_geometry: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326),
        name="value_geom",
        nullable=True,
        doc="Geometry value of the attribute.",
    )

    # Foreign key to Entity.
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entity.id"),
        nullable=False,
        doc="Reference to the entity that this attribute belongs to.",
    )

    # Back reference to the parent Entity.
    entity: Mapped["Entity"] = relationship("Entity", back_populates="attributes")

    @property
    def value(self):
        """Return the stored value based on the attribute's type."""
        if self.type == AttributeType.STRING:
            return self.value_str
        elif self.type == AttributeType.INTEGER:
            return self.value_int
        elif self.type == AttributeType.FLOAT:
            return self.value_float
        elif self.type == AttributeType.BOOLEAN:
            return self.value_boolean
        elif self.type == AttributeType.DATE:
            return self.value_date
        elif self.type == AttributeType.ENUM:
            return self.value_enum
        elif self.type == AttributeType.GEOMETRY:
            return mapping(to_shape(self.value_geometry))
        return None

    @value.setter
    def value(self, new_value):
        if isinstance(new_value, bool):
            self.value_boolean = new_value
            self.type = AttributeType.BOOLEAN
        elif isinstance(new_value, int):
            self.value_int = new_value
            self.type = AttributeType.INTEGER
        elif isinstance(new_value, float):
            self.value_float = new_value
            self.type = AttributeType.FLOAT
        elif isinstance(new_value, date):
            self.value_date = new_value
            self.type = AttributeType.DATE
        elif isinstance(new_value, Enum):
            self.value_enum = new_value.name
            self.type = AttributeType.ENUM
        elif isinstance(new_value, dict):
            try:
                self.value_geometry = from_shape(shape(new_value), srid=4326)
                self.type = AttributeType.GEOMETRY
            except (ValidationError, ValueError) as e:
                raise ValueError("Invalid geometry value.")

        elif isinstance(new_value, str):
            self.value_str = new_value
            self.type = AttributeType.STRING
        else:
            raise ValueError("Unsupported type for attribute value.")
