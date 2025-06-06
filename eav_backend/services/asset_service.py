import hashlib
import logging
import uuid

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session, aliased

from eav_backend.models import (
    Asset,
    EntityDefinition,
    EntityRelation,
    Entity,
    AssetContent,
)


class AssetService:

    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger("openepi")

    def get_assets_for_entity(self, entity_id: str) -> list[Asset]:
        query = self.session.query(Asset).filter(Asset.entity_id == entity_id)

        return query.all()

    def get_asset_by_id(self, asset_id: uuid.UUID) -> Asset:
        return self.session.query(Asset).filter(Asset.id == asset_id).first()

    def get_assets_by_id_and_path(
        self, ed: EntityDefinition, **filters
    ) -> list["Asset"]:
        identifier = filters.pop(ed.identifier)

        # Query assets linked to the entity directly
        query = self.session.query(Asset).filter(
            Asset.entity_id == uuid.UUID(identifier)
        )

        # Alias starting from the entity linked to the asset
        current_alias = aliased(Entity, name="entity_final")
        query = query.join(current_alias, Asset.entity_id == current_alias.id)
        query = query.filter(
            current_alias.entity_type == ed.name, current_alias.is_deleted == False
        )

        # Walk up the parent chain
        for i, (parent_type, parent_id) in enumerate(reversed(list(filters.items()))):
            relation_alias = aliased(EntityRelation, name=f"relation_alias_{i}")
            parent_alias = aliased(Entity, name=f"parent_alias_{i}")

            query = (
                query.join(
                    relation_alias, current_alias.id == relation_alias.target_entity_id
                )
                .filter(relation_alias.is_deleted == False)
                .join(parent_alias, relation_alias.source_entity_id == parent_alias.id)
                .filter(
                    parent_alias.entity_type == parent_type.capitalize(),
                    parent_alias.id == uuid.UUID(parent_id),
                    parent_alias.is_deleted == False,
                )
            )

            current_alias = parent_alias

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                query.statement.compile(
                    dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
                )
            )

        return query.all()

    def add_asset_for_id_and_path(
        self,
        entity_definition: EntityDefinition,
        asset: Asset,
        contents: bytes,
        **param_dict,
    ):

        entity_identifier = param_dict.get(entity_definition.identifier)
        asset.entity_id = uuid.UUID(entity_identifier)
        asset.content = AssetContent(content=contents)
        asset.checksum = hashlib.sha256(contents).hexdigest()

        self.session.add(asset)
        self.session.flush()
        self.session.commit()
        return asset
