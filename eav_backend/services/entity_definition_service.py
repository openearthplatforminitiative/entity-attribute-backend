import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from eav_backend.models import EntityDefinition, AttributeDefinition

logger = logging.getLogger(__name__)


class EntityDefinitionService:

    def __init__(self, session):
        self.session = session

    def get_entity_definitions(self) -> List[EntityDefinition]:
        stmt = select(EntityDefinition).options(
            joinedload(EntityDefinition.required_attributes),
            joinedload(EntityDefinition.optional_attributes),
        )
        return self.session.scalars(stmt).unique().all()

    def get_entity_definition(self, id) -> Optional[EntityDefinition]:
        stmt = (
            select(EntityDefinition)
            .options(
                joinedload(EntityDefinition.required_attributes),
                joinedload(EntityDefinition.optional_attributes),
            )
            .where(EntityDefinition.id == id)
        )

        return self.session.scalars(stmt).unique().one_or_none()

    def find_entity_definition_with_name(self, name) -> Optional[EntityDefinition]:
        stmt = select(EntityDefinition).where(EntityDefinition.name == name)
        return self.session.scalars(stmt).unique().one_or_none()

    def find_attribute_definition_by_name_and_type(
        self, name, type
    ) -> Optional[AttributeDefinition]:
        stmt = select(AttributeDefinition).where(
            (AttributeDefinition.name == name) & (AttributeDefinition.type == type)
        )
        return self.session.scalars(stmt).unique().one_or_none()

    def _replace_attributes(
        self, attributes: List[AttributeDefinition]
    ) -> List[AttributeDefinition]:
        """Helper method to replace each attribute with an existing one if available."""
        return [
            self.find_attribute_definition_by_name_and_type(attr.name, attr.type)
            or attr
            for attr in attributes
        ]

    def create_entity_definition(
        self, entity_definition: EntityDefinition
    ) -> EntityDefinition:

        entity_definition.required_attributes = self._replace_attributes(
            entity_definition.required_attributes
        )
        entity_definition.optional_attributes = self._replace_attributes(
            entity_definition.optional_attributes
        )

        self.session.add(entity_definition)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return entity_definition
