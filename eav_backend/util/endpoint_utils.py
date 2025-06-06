from inspect import Parameter, Signature
from typing import Callable, Optional

from fastapi import UploadFile, File
from fastapi.params import Depends

from eav_backend.dependencies import get_entity_service
from eav_backend.services.entity_service import EntityService


def build_signature(
    path_params: list[str],
    file_param: bool = False,
    include_body: bool = False,
    body_type=None,
    body_name: str = "item",
    service: Callable = get_entity_service,
) -> Signature:
    params = []

    if include_body and body_type:
        params.append(
            Parameter(
                name=body_name,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=body_type,
            )
        )

    for param in path_params:
        params.append(
            Parameter(name=param, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
        )

    if file_param:
        params.append(
            Parameter(
                name="file",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=UploadFile,
                default=File(...),
            )
        )

    params.append(
        Parameter(
            name="service",
            kind=Parameter.KEYWORD_ONLY,
            annotation=EntityService,
            default=Depends(service),
        )
    )

    return Signature(parameters=params)


def create_endpoint_wrapper(
    handler: Callable,
    *,
    http_method: str,
    path_params: Optional[list[str]] = None,
    upload_file: bool = False,
    include_body: bool = False,
    body_type=None,
    response_model=None,
    entity_definition=None,
    relation_collection: Optional[str] = None,
    service: Callable = get_entity_service,
):
    path_params = path_params or []

    async def endpoint(**kwargs):
        service = kwargs.pop("service")
        item = kwargs.get("item") if include_body else None
        file = kwargs.get("file") if upload_file else None
        param_values = [kwargs[param] for param in path_params]
        return await handler(
            item=item,
            file=file,
            response_model=response_model,
            entity_definition=entity_definition,
            service=service,
            path_params=path_params,
            param_values=param_values,
            relation_collection=relation_collection,
        )

    endpoint.__signature__ = build_signature(
        path_params=path_params,
        file_param=upload_file,
        include_body=include_body,
        body_type=body_type,
        service=service,
    )
    endpoint.__name__ = f"{http_method}_endpoint_with_" + "_".join(path_params)
    return endpoint
