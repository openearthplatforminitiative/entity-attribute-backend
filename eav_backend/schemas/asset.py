import uuid
from datetime import datetime
from typing import Optional

from pydantic import Field, HttpUrl

from eav_backend.schemas.basemodel import BaseModel


class Asset(BaseModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique identifier for the asset."
    )
    name: str = Field(description="The name of the file asset.")
    mimetype: str = Field(
        description="The MIME type of the file (e.g., application/pdf, image/png)."
    )
    file_size: int = Field(description="The size of the file in bytes.")
    url: HttpUrl = Field(description="The URL where the file is stored.")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp when the asset was created.",
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="The timestamp when the asset was last updated."
    )
    checksum: Optional[str] = Field(
        default=None, description="A checksum to verify the integrity of the file."
    )
