import logging
import uuid
from typing import Optional

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import aliased

from eav_backend.models import Entity, EntityRelation, EntityDefinition


class EntityService:

    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger("openepi")

    def create_entity(
        self,
        entity: Entity,
        relations: dict[str, str],
        relation_collection: str = None,
    ) -> Entity:
        self.session.add(entity)
        self.session.flush()

        if relations:
            immediate_parent_type = list(relations.keys())[-1]
            immediate_parent_id = list(relations.values())[-1]
            parent_entity: Entity = (
                self.session.query(Entity)
                .filter(Entity.id == immediate_parent_id)
                .first()
            )

            if not parent_entity or not parent_entity.is_of_type(immediate_parent_type):
                raise Exception(
                    f"Parent entity with id {immediate_parent_id} of type {immediate_parent_type} not found."
                )
            else:
                parent_entity.relations.append(
                    EntityRelation(
                        target_entity=entity,
                        collection_name=relation_collection,
                    )
                )

        self.session.commit()

        return entity

    def get_entities_by_type(self, entity_type: str, **filters) -> list[Entity]:
        # Start by querying for the final entity type (e.g. "incident").
        query = self.session.query(Entity).filter(
            Entity.entity_type == entity_type, Entity.is_deleted == False
        )
        # We'll use this alias to represent the "child" in the join.
        current_alias = Entity

        # The filters come in as a dict with outermost keys first.
        # We reverse the order so that we join from the final entity upward.
        for i, (parent_type, parent_id) in enumerate(reversed(list(filters.items()))):
            relation_alias = aliased(EntityRelation, name=f"relation_alias_{i}")
            parent_alias = aliased(Entity, name=f"parent_alias_{i}")
            # Join from the current entity (child) to the association table,
            # linking current_alias.id == relation_alias.target_entity_id.
            query = query.join(
                relation_alias, current_alias.id == relation_alias.target_entity_id
            )

            # Make sure relation is not deleted.
            query = query.filter(relation_alias.is_deleted == False)

            # Then join from the association table to the parent entity.
            query = query.join(
                parent_alias, relation_alias.source_entity_id == parent_alias.id
            )
            # Filter on the parent's type and id.
            query = query.filter(
                parent_alias.entity_type == parent_type.capitalize(),
                parent_alias.id == parent_id,
            )
            # Set current_alias to this parent so that the next iteration will join upward.
            current_alias = parent_alias

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                query.statement.compile(
                    dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
                )
            )

        return query.all()

    def get_entity_by_type_and_path(
        self,
        ed: EntityDefinition,
        **filters,
    ) -> Optional[Entity]:
        identifier = filters.pop(ed.identifier)

        query = self.session.query(Entity).filter(
            Entity.entity_type == ed.name,
            Entity.id == uuid.UUID(identifier),
            Entity.is_deleted == False,
        )

        current_alias = Entity

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

        return query.first()

    def update_entity(self, entity, relations, relation_collection) -> Entity:

        if len(relations) > 1:
            immediate_parent_type = list(relations.keys())[-2]
            immediate_parent_id = list(relations.values())[-2]

            parent_entity: Entity = (
                self.session.query(Entity)
                .filter(Entity.id == immediate_parent_id)
                .first()
            )

            if not parent_entity or not parent_entity.is_of_type(immediate_parent_type):
                raise Exception(
                    f"Parent entity with id {immediate_parent_id} of type {immediate_parent_type} not found."
                )

            # Ensure the relation actually exists
            relation: EntityRelation = (
                self.session.query(EntityRelation)
                .filter_by(
                    source_entity_id=parent_entity.id,
                    target_entity_id=entity.id,
                    collection_name=relation_collection,
                )
                .first()
            )
            if relation:
                relation.is_deleted = entity.is_deleted
            else:
                raise Exception(
                    f"No existing relation from parent {immediate_parent_id} to entity {entity.id} with collection {relation_collection}."
                )

        self.session.flush()
        self.session.commit()
        return entity
