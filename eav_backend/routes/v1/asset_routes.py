import logging
import uuid

from fastapi import UploadFile, HTTPException, APIRouter, Depends
from fastapi.responses import StreamingResponse

from eav_backend.config import settings
from eav_backend.dependencies import get_asset_service
from eav_backend.models import EntityDefinition
from eav_backend.schemas.asset import Asset as SchemaAsset
from eav_backend.models.asset import Asset as ModelAsset
from eav_backend.services.asset_service import AssetService

logger = logging.getLogger("openepi")
router = APIRouter(prefix="/assets")


async def get_assets(
    entity_definition: EntityDefinition,
    service: AssetService,
    path_params: list[str],
    param_values: list[str],
    **kwargs,
):
    param_dict = {}
    if path_params and param_values:
        param_dict = dict(zip(path_params, param_values))
    logger.info(
        f"Getting assets for entity with id {param_dict.get(entity_definition.identifier)}"
    )
    assets = service.get_assets_by_id_and_path(entity_definition, **param_dict)
    return [SchemaAsset.model_validate(asset) for asset in assets]


async def add_asset(
    entity_definition: EntityDefinition,
    file: UploadFile,
    path_params: list[str],
    param_values: list[str],
    relation_collection: str,
    service: AssetService,
    **kwargs,
):
    param_dict = {}
    if path_params and param_values:
        param_dict = dict(zip(path_params, param_values))

    file.file.seek(0, 2)  # Move to the end of the file to get its size
    file_size = file.file.tell()
    file.file.seek(0)  # Reset the file pointer to the beginning

    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds the maximum allowed limit of {settings.max_upload_size} bytes",
        )

    logger.info(
        f"Adding asset with file size {file_size} for entity with id {param_dict.get(entity_definition.identifier)}"
    )
    file_contents = await file.read()

    asset = service.add_asset_for_id_and_path(
        entity_definition,
        ModelAsset(name=file.filename, mimetype=file.content_type, file_size=file_size),
        file_contents,
        **param_dict,
    )

    return SchemaAsset.model_validate(asset)


@router.get(
    "/{asset_id}",
    summary="Get asset content",
    response_class=StreamingResponse,
    tags=["assets"],
)
async def get_asset_content(
    asset_id: uuid.UUID, service: AssetService = Depends(get_asset_service)
):
    asset = service.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=404, detail=f"Asset with id {asset_id} not found"
        )

    return StreamingResponse(
        iter([asset.content.content]),
        media_type=asset.mimetype,
        headers={"Content-Disposition": f"filename={asset.name}"},
    )
