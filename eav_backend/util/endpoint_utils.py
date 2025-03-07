from inspect import Parameter, Signature
from typing import Callable, Optional

from fastapi.params import Depends

from eav_backend.dependencies import get_entity_service
from eav_backend.services.entity_service import EntityService


def build_signature(
    path_params: list[str],
    include_body: bool = False,
    body_type=None,
    body_name: str = "item",
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

    params.append(
        Parameter(
            name="service",
            kind=Parameter.KEYWORD_ONLY,
            annotation=EntityService,
            default=Depends(get_entity_service),
        )
    )

    return Signature(parameters=params)


def create_endpoint_wrapper(
    handler: Callable,
    *,
    http_method: str,
    path_params: Optional[list[str]] = None,
    include_body: bool = False,
    body_type=None,
    response_model=None,
    entity_definition=None,
    relation_collection: Optional[str] = None,
):
    path_params = path_params or []

    async def endpoint(**kwargs):
        service = kwargs.pop("service")
        item = kwargs.get("item") if include_body else None
        param_values = [kwargs[param] for param in path_params]
        return await handler(
            item=item,
            response_model=response_model,
            entity_definition=entity_definition,
            service=service,
            path_params=path_params,
            param_values=param_values,
            relation_collection=relation_collection,
        )

    endpoint.__signature__ = build_signature(
        path_params=path_params,
        include_body=include_body,
        body_type=body_type,
    )
    endpoint.__name__ = f"{http_method}_endpoint_with_" + "_".join(path_params)
    return endpoint
