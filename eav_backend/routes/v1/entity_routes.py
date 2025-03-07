import logging
from http import HTTPStatus

from fastapi import HTTPException
from pydantic.main import ModelT

from eav_backend.builders.EntityBuilder import EntityBuilder
from eav_backend.models import EntityDefinition, Entity
from eav_backend.services.entity_service import EntityService

logger = logging.getLogger("openepi")


async def get_entities(
    response_model: type[ModelT],
    entity_definition: EntityDefinition,
    service: EntityService,
    path_params: list[str],
    param_values: list[str],
    **kwargs,
) -> list[ModelT]:
    logger.info("Getting entities")

    entities = service.get_entities_by_type(
        entity_type=entity_definition.name,
        **dict(zip(path_params, param_values)),
    )

    resp_dicts = []
    for entity in entities:
        resp_dicts.append(
            response_model.model_validate(
                EntityBuilder.to_dict(entity, entity_definition)
            )
        )

    return resp_dicts


async def get_entity(
    response_model: type[ModelT],
    service: EntityService,
    entity_definition: EntityDefinition,
    path_params: list[str],
    param_values: list[str],
    **kwargs,
) -> ModelT:
    param_dict = {}
    if path_params and param_values:
        param_dict = dict(zip(path_params, param_values))
    logger.info(
        f"Posting entity of type {entity_definition.name} with params {param_dict}"
    )

    entity = service.get_entity_by_type_and_path(entity_definition, **param_dict)

    if entity:
        return response_model.model_validate(
            EntityBuilder.to_dict(entity, entity_definition)
        )
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Entity with id {param_dict.get(entity_definition.identifier)} of type {entity_definition.name} not found",
        )


async def add_entity(
    item: type[ModelT],
    response_model: type[ModelT],
    entity_definition: EntityDefinition,
    service: EntityService,
    path_params: list[str],
    param_values: list[str],
    relation_collection: str = None,
) -> ModelT:
    param_dict = {}
    if path_params and param_values:
        param_dict = dict(zip(path_params, param_values))
    logger.info(
        f"Posting entity of type {entity_definition.name} with params {param_dict}"
    )

    saved_entity = service.create_entity(
        entity=EntityBuilder.to_entity(entity_definition, item),
        relations=param_dict,
        relation_collection=relation_collection,
    )
    response_data = EntityBuilder.to_dict(saved_entity, entity_definition)
    validated_model = response_model.model_validate(response_data)
    return validated_model


async def update_entity(
    item: type[ModelT],
    response_model: type[ModelT],
    entity_definition: EntityDefinition,
    service: EntityService,
    path_params: list[str],
    param_values: list[str],
    relation_collection: str = None,
) -> ModelT:
    param_dict = {}
    if path_params and param_values:
        param_dict = dict(zip(path_params, param_values))
    logger.info(
        f"Updating entity of type {entity_definition.name} with params {param_dict}"
    )

    entity_id: str = param_dict.get(entity_definition.identifier)
    to_update: Entity = service.get_entity_by_type_and_path(
        entity_definition, **param_dict
    )
    if not to_update:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Entity with id {entity_id} of type {entity_definition.name} not found",
        )

    merged: Entity = EntityBuilder.merge(
        to_update, EntityBuilder.to_entity(entity_definition, item)
    )

    updated_entity = service.update_entity(
        entity=merged,
        relations=param_dict,
        relation_collection=relation_collection,
    )

    response_data = EntityBuilder.to_dict(updated_entity, entity_definition)
    validated_model = response_model.model_validate(response_data)

    return validated_model


async def delete_entity(
    entity_definition: EntityDefinition,
    service: EntityService,
    path_params: list[str],
    param_values: list[str],
    relation_collection: str = None,
    **kwargs,
):
    param_dict = {}
    if path_params and param_values:
        param_dict = dict(zip(path_params, param_values))

    identifier: str = param_dict.get(entity_definition.identifier)

    entity = service.get_entity_by_type_and_path(entity_definition, **param_dict)
    if not entity:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Entity with id {identifier} of type {entity_definition.name} not found",
        )

    entity.is_deleted = True
    service.update_entity(entity, param_dict, relation_collection)
