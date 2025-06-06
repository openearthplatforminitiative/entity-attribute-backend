import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from eav_backend.dependencies import (
    get_entity_definition_service,
    get_entity_import_service,
)
from eav_backend.models.exceptions import ExistsException
from eav_backend.schemas.entity_definition import (
    EntityDefinitionResponse,
    EntityDefinitionRequest,
)
from eav_backend.services.dynamic_model_service import DynamicModelService
from eav_backend.services.entity_definition_service import EntityDefinitionService
from eav_backend.services.entity_import_service import EntityImportService

router = APIRouter()
logger = logging.getLogger("openepi")


@router.get(
    "/v1/admin/entity_definitions",
    summary="Get all entity definitions",
    description="Returns all entity definitions from the metadata store",
    tags=["admin"],
    response_model=List[EntityDefinitionResponse],
    response_model_exclude_none=True,
)
async def get_entity_definitions(
    service: EntityDefinitionService = Depends(get_entity_definition_service),
) -> List[EntityDefinitionResponse]:
    return [
        EntityDefinitionResponse.model_validate(entity)
        for entity in service.get_entity_definitions()
    ]


@router.get(
    "/v1/admin/entity_definitions/{id}",
    summary="Get entity definition",
    description="Returns the entity definition from the metadata store",
    tags=["admin"],
    response_model=EntityDefinitionResponse,
    response_model_exclude_none=True,
)
async def get_entity_definition(
    id: uuid.UUID,
    service: EntityDefinitionService = Depends(get_entity_definition_service),
) -> Optional[EntityDefinitionResponse]:
    ed = service.get_entity_definition(id)
    if not ed:
        raise HTTPException(
            status_code=404, detail=f"Entity definition with id {id} not found"
        )
    return EntityDefinitionResponse.model_validate(ed)


@router.post(
    "/v1/admin/entity_definitions",
    summary="Create entity definition",
    tags=["admin"],
    response_model=EntityDefinitionResponse,
)
async def create_entity_definition(
    entity_definition_req: EntityDefinitionRequest,
    request: Request,
    service: EntityImportService = Depends(get_entity_import_service),
) -> EntityDefinitionResponse:

    try:
        imported_entity = service.import_entity(entity_definition_req)
        DynamicModelService(
            service.entity_definition_service, request.app
        ).build_models_from_entity_definitions()
        return imported_entity
    except ExistsException as e:
        raise HTTPException(status_code=409, detail=e.msg)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Unknown error")
