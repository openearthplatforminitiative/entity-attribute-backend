from typing import Any

from pydantic.main import ModelT

from eav_backend.models import EntityDefinition, Entity, Attribute, EntityRelation


class EntityBuilder:

    @staticmethod
    def to_entity(ed: EntityDefinition, item: type[ModelT]) -> Entity:
        main_entity = Entity(entity_type=ed.name)
        main_attributes = item.model_dump(
            exclude=set([x.collection_name for x in ed.entity_relations])
        )

        attrs = []
        for attr_name in [x for x in main_attributes if main_attributes[x] is not None]:
            attribute = Attribute(name=attr_name)
            attribute.value = main_attributes[attr_name]
            attrs.append(attribute)

        main_entity.attributes = attrs
        main_entity.relations = []

        for relation_def in ed.entity_relations:
            relations = getattr(item, relation_def.collection_name, [])
            for relation in relations if relations else []:
                main_entity.relations.append(
                    EntityRelation(
                        target_entity=EntityBuilder.to_entity(
                            relation_def.target_entity, relation
                        ),
                        collection_name=relation_def.collection_name,
                    )
                )

        return main_entity

    @staticmethod
    def to_dict(entity: Entity, entity_definition: EntityDefinition) -> dict[str, Any]:
        response_data: dict[str, Any] = {"id": entity.id}

        for attr in entity.attributes:
            response_data[attr.name] = attr.value

        for relation in entity.relations:
            response_data[relation.collection_name] = response_data.get(
                relation.collection_name, []
            )
            response_data[relation.collection_name].append(
                EntityBuilder.to_dict(relation.target_entity, entity_definition)
            )

        return response_data

    @classmethod
    def merge(cls, to_update: Entity, with_new_values: Entity) -> Entity:
        for attr in with_new_values.attributes:
            existing_attr = next(
                (a for a in to_update.attributes if a.name == attr.name), None
            )
            if existing_attr:
                existing_attr.value = attr.value
            else:
                to_update.attributes.append(attr)

        for relation in with_new_values.relations:
            existing_relation = next(
                (
                    r
                    for r in to_update.relations
                    if r.collection_name == relation.collection_name
                ),
                None,
            )
            if existing_relation:
                existing_relation.target_entity = cls.merge(
                    existing_relation.target_entity, relation.target_entity
                )
            else:
                to_update.relations.append(relation)

        return to_update
