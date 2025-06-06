from fastapi.params import Depends
from sqlalchemy.orm import Session

from eav_backend.config import settings
from eav_backend.database import SessionLocal
from eav_backend.services.entity_definition_service import EntityDefinitionService
from eav_backend.services.entity_import_service import EntityImportService
from eav_backend.services.entity_service import EntityService


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_entity_definition_service(
    db: Session = Depends(get_db),
) -> EntityDefinitionService:
    return EntityDefinitionService(db)


def get_entity_service(
    db: Session = Depends(get_db),
) -> EntityService:
    return EntityService(db)


def get_entity_import_service(
    eds: EntityDefinitionService = Depends(get_entity_definition_service),
) -> EntityImportService:
    return EntityImportService(eds, settings.import_config)
