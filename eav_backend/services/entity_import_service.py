import hashlib
import logging

from fastapi import HTTPException
from pathlib import Path

from eav_backend.config import settings
from eav_backend.models import (
    EntityDefinition,
    AttributeDefinition,
    EntityRelationDefinition,
)
from eav_backend.models.exceptions import ExistsException
from eav_backend.schemas.entity_definition import (
    EntityDefinitionRequest,
    EntityDefinitionResponse,
)
from eav_backend.schemas.entity_relation import EntityRelationRequest
from eav_backend.services.entity_definition_service import EntityDefinitionService


def md5(entity_definition_req: EntityDefinitionRequest) -> str:
    return hashlib.md5(
        entity_definition_req.model_dump_json().encode("UTF-8")
    ).hexdigest()


class EntityImportService:
    def __init__(self, entity_definition_service: EntityDefinitionService):
        self.entity_definition_service = entity_definition_service
        self.logger = logging.getLogger("openepi")

    def import_entities(self):
        if settings.import_entities:
            self.logger.info(f"Importing entities from {settings.import_config}")
            path = Path(settings.import_config)
            if not path.exists():
                self.logger.error(
                    f"Import path {settings.import_config} does not exist"
                )
                raise ImportError(
                    f"Import path {settings.import_config} does not exist"
                )

            for entity_file in sorted(list(path.glob("*.json"))):
                entity_definition_req = EntityDefinitionRequest.model_validate_json(
                    entity_file.read_text()
                )
                self.import_entity(entity_definition_req)

    def import_entity(self, entity_definition_req: EntityDefinitionRequest):
        req_hash = md5(entity_definition_req)
        existing = self.entity_definition_service.find_entity_definition_with_name(
            entity_definition_req.name
        )
        needs_update = req_hash != existing.hash if existing else False

        if existing:
            return (
                self.update_entity(entity_definition_req) if needs_update else existing
            )
        else:
            ed = EntityDefinition(
                **entity_definition_req.model_dump(
                    exclude={
                        "required_attributes",
                        "optional_attributes",
                        "related_entities",
                    }
                ),
                hash=req_hash,
                required_attributes=[
                    AttributeDefinition(**attr.model_dump())
                    for attr in entity_definition_req.required_attributes
                ],
                optional_attributes=[
                    AttributeDefinition(**attr.model_dump())
                    for attr in entity_definition_req.optional_attributes
                ],
                entity_relations=[
                    self.get_related_entity(x)
                    for x in entity_definition_req.related_entities
                ],
            )

            return EntityDefinitionResponse.model_validate(
                self.entity_definition_service.create_entity_definition(ed)
            )

    def update_entity(self, entity_definition_req):
        if not settings.update_entities:
            raise ExistsException(
                f"Entity definition with name {entity_definition_req.name} was changed, but update_entities is False"
            )
        else:
            raise NotImplementedError("No support for updating entities yet")

    def get_related_entity(
        self, entity_relation_req: EntityRelationRequest
    ) -> EntityRelationDefinition:
        related_entity = (
            self.entity_definition_service.find_entity_definition_with_name(
                entity_relation_req.entity
            )
        )

        if not related_entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity definition with name {entity_relation_req.entity} not found",
            )

        return EntityRelationDefinition(
            target_entity_id=related_entity.id,
            collection_name=entity_relation_req.collection_name,
            api_endpoints=entity_relation_req.api_endpoints or [],
        )
