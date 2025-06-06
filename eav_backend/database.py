import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from eav_backend.config import settings

engine = create_engine(settings.database_connection, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )
    type_annotation_map = {
        datetime: postgresql.TIMESTAMP(timezone=True),
        dict[str, Any]: postgresql.JSONB,
        uuid.UUID: postgresql.UUID,
    }
