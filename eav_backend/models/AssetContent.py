from sqlalchemy import Column, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from eav_backend.models import Base


class AssetContent(Base):
    __tablename__ = "asset_content"

    asset_id = Column(
        ForeignKey("asset.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    content = Column(LargeBinary, nullable=False)

    asset = relationship("Asset", back_populates="content")
