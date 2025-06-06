import uuid
from datetime import date
from typing import Optional, List

from fastapi import FastAPI, Response
from geojson_pydantic.geometries import Geometry
from pydantic import create_model
from pydantic.main import ModelT

from eav_backend.config import settings
from eav_backend.dependencies import get_asset_service
from eav_backend.models import EntityDefinition
from eav_backend.routes.v1.asset_routes import get_assets, add_asset
from eav_backend.routes.v1.entity_routes import (
    get_entity,
    add_entity,
    update_entity,
    delete_entity,
)
from eav_backend.schemas.asset import Asset
from eav_backend.schemas.basemodel import BaseModel
from eav_backend.services.entity_definition_service import (
    EntityDefinitionService,
)
from eav_backend.util.endpoint_utils import create_endpoint_wrapper

type_mapping = {
    "STRING": str,
    "INTEGER": int,
    "FLOAT": float,
    "BOOLEAN": bool,
    "DATE": date,
    "ENUM": str,
    "UUID": uuid.UUID,
    "GEOMETRY": Geometry,
}


class BuiltModel:
    request_model: type[ModelT]
    response_model: type[ModelT]
    summary_model: type[ModelT] | None
    return_summary_on_collection: bool = False

    def __init__(
        self,
        request_model: type[ModelT],
        response_model: type[ModelT],
        summary_model: type[ModelT] | None,
        return_summary_on_collection: bool,
    ):
        self.request_model = request_model
        self.response_model = response_model
        self.summary_model = summary_model
        self.return_summary_on_collection = return_summary_on_collection

    @property
    def collection_model(self) -> type[ModelT]:
        if self.return_summary_on_collection:
            return self.summary_model
        return self.response_model


class DynamicModelService:

    def __init__(
        self, entity_definition_service: EntityDefinitionService, app: FastAPI
    ):
        self.app = app
        self.entity_definition_service = entity_definition_service
        self.built_models: dict[str, BuiltModel] = {}

    def build_models_from_entity_definitions(self):
        for ed in self.entity_definition_service.get_entity_definitions():
            self.build_model(ed)
            self.build_api_endpoints(
                ed,
                tag=ed.collection_name,
                root_path=f"/v1/{ed.collection_name}",
                api_endpoints=ed.api_endpoints,
                parent_api_endpoints=["LIST"],
            )

    def build_model(self, entity_definition: EntityDefinition) -> BuiltModel:
        if entity_definition.name in self.built_models:
            return self.built_models[entity_definition.name]
        else:
            summary_model = None
            request_fields = {}
            response_fields = {}
            summary_fields = {}
            fields = {}
            for attribute in entity_definition.required_attributes:
                py_type = type_mapping.get(attribute.type, str)
                fields[attribute.name] = (py_type, None)
                if attribute.include_in_summary:
                    summary_fields[attribute.name] = (py_type, None)

            for attribute in entity_definition.optional_attributes:
                py_type = type_mapping.get(attribute.type, str)
                fields[attribute.name] = (Optional[py_type], None)

            related_models: list[BuiltModel] = []
            for relation in entity_definition.entity_relations:
                related_built_model = self.build_model(relation.target_entity)
                self.built_models[relation.target_entity.name] = related_built_model
                related_models.append(related_built_model)
                request_fields[relation.collection_name] = (
                    List[related_built_model.request_model],
                    None,
                )
                response_fields[relation.collection_name] = (
                    List[related_built_model.response_model],
                    None,
                )

            request_model = create_model(
                f"{entity_definition.name}Request",
                __base__=BaseModel,
                **fields | request_fields,
            )

            response_fields["id"] = (uuid.UUID, None)
            summary_fields["id"] = (uuid.UUID, None)
            response_model = create_model(
                f"{entity_definition.name}Response",
                __base__=BaseModel,
                **fields | response_fields,
            )

            if entity_definition.return_summary_on_collection:
                summary_model = create_model(
                    f"{entity_definition.name}Summary",
                    __base__=BaseModel,
                    **summary_fields,
                )

            built_model = BuiltModel(
                request_model,
                response_model,
                summary_model,
                entity_definition.return_summary_on_collection,
            )
            self.built_models[entity_definition.name] = built_model
            return built_model

    def build_api_endpoints(
        self,
        ed: EntityDefinition,
        tag: str,
        root_path: str = "/v1",
        api_endpoints: list = [],
        parent_api_endpoints: list = None,
        relation_collection: str = None,
        path_params: list = [],
    ):

        model = self.built_models[ed.name]

        if "LIST" in parent_api_endpoints:
            if "LIST" in api_endpoints:
                self.add_get_collection_endpoint(ed, model, root_path, tag, path_params)

            if "POST" in api_endpoints:
                self.add_post_collection_endpoint(
                    ed, model, root_path, tag, path_params, relation_collection
                )

            if "GET" in api_endpoints:
                self.add_get_entity_endpoint(
                    ed,
                    model,
                    f"{root_path}/{{{ed.identifier}}}",
                    tag,
                    path_params + [ed.identifier],
                )

            if "PUT" in api_endpoints:
                self.add_put_entity_endpoint(
                    ed,
                    model,
                    f"{root_path}/{{{ed.identifier}}}",
                    tag,
                    path_params + [ed.identifier],
                    relation_collection,
                )

            if "DELETE" in api_endpoints:
                self.add_delete_entity_endpoint(
                    ed,
                    model,
                    f"{root_path}/{{{ed.identifier}}}",
                    tag,
                    path_params + [ed.identifier],
                    relation_collection,
                )

            if ed.supports_assets and settings.enable_assets:
                self.add_asset_endpoints(
                    ed,
                    model,
                    f"{root_path}/{{{ed.identifier}}}",
                    tag,
                    path_params + [ed.identifier],
                    relation_collection,
                )

        for relation in ed.entity_relations:
            self.build_api_endpoints(
                relation.target_entity,
                tag=tag,
                root_path=f"{root_path}/{{{ed.identifier}}}/{relation.collection_name}",
                path_params=path_params + [ed.identifier],
                api_endpoints=relation.api_endpoints,
                parent_api_endpoints=api_endpoints,
                relation_collection=relation.collection_name,
            )

    def add_get_collection_endpoint(
        self, entity_definition, model, root_path, tag, path_params
    ):
        from eav_backend.routes.v1.entity_routes import get_entities

        self.app.add_api_route(
            path=root_path,
            response_model=List[model.collection_model],
            methods=["GET"],
            tags=[tag],
            name=f"get_{entity_definition.collection_name}",
            description=f"Get all {entity_definition.collection_name}",
            endpoint=create_endpoint_wrapper(
                get_entities,
                http_method="GET",
                path_params=path_params,
                response_model=model.collection_model,
                entity_definition=entity_definition,
            ),
        )

    def add_post_collection_endpoint(
        self,
        entity_definition,
        model,
        root_path,
        tag,
        path_params,
        relation_collection: str = None,
    ):

        self.app.add_api_route(
            path=root_path,
            response_model=model.response_model,
            methods=["POST"],
            tags=[tag],
            name=f"add_{entity_definition.name}",
            description=f"Add a new {entity_definition.name}",
            endpoint=create_endpoint_wrapper(
                handler=add_entity,
                http_method="POST",
                path_params=path_params,
                include_body=True,
                body_type=model.request_model,
                response_model=model.response_model,
                entity_definition=entity_definition,
                relation_collection=relation_collection,
            ),
        )

    def add_get_entity_endpoint(
        self,
        entity_definition,
        model,
        root_path,
        tag,
        path_params,
    ):
        self.app.add_api_route(
            path=root_path,
            response_model=model.response_model,
            methods=["GET"],
            tags=[tag],
            name=f"Get_{entity_definition.name}",
            description=f"Get a(n) {entity_definition.name}",
            endpoint=create_endpoint_wrapper(
                get_entity,
                http_method="GET",
                path_params=path_params,
                response_model=model.response_model,
                entity_definition=entity_definition,
            ),
        )

    def add_put_entity_endpoint(
        self,
        entity_definition,
        model,
        root_path,
        tag,
        path_params,
        relation_collection: str = None,
    ):
        self.app.add_api_route(
            path=root_path,
            response_model=model.response_model,
            methods=["PUT"],
            tags=[tag],
            name=f"update_{entity_definition.name}",
            description=f"Update a(n) {entity_definition.name}",
            endpoint=create_endpoint_wrapper(
                handler=update_entity,
                http_method="PUT",
                path_params=path_params,
                include_body=True,
                body_type=model.request_model,
                response_model=model.response_model,
                entity_definition=entity_definition,
                relation_collection=relation_collection,
            ),
        )

    def add_delete_entity_endpoint(
        self,
        entity_definition,
        model,
        root_path,
        tag,
        path_params,
        relation_collection: str = None,
    ):
        self.app.add_api_route(
            path=root_path,
            response_class=Response,
            status_code=204,
            responses={204: {}, 404: {}},
            methods=["DELETE"],
            tags=[tag],
            name=f"delete_{entity_definition.name}",
            description=f"Delete a(n) {entity_definition.name}",
            endpoint=create_endpoint_wrapper(
                handler=delete_entity,
                http_method="DELETE",
                path_params=path_params,
                entity_definition=entity_definition,
                relation_collection=relation_collection,
            ),
        )

    def add_asset_endpoints(
        self,
        entity_definition,
        model,
        root_path,
        tag,
        path_params,
        relation_collection=None,
    ):
        self.app.add_api_route(
            path=f"{root_path}/assets",
            response_model=List[Asset],
            methods=["GET"],
            tags=[tag],
            name=f"get_{entity_definition.name}_assets",
            description=f"Get assets for {entity_definition.name}",
            endpoint=create_endpoint_wrapper(
                handler=get_assets,  # Replace with the actual handler for assets
                http_method="GET",
                path_params=path_params,
                response_model=List[Asset],
                entity_definition=entity_definition,
                relation_collection=relation_collection,
                service=get_asset_service,
            ),
        )
        self.app.add_api_route(
            path=f"{root_path}/assets",
            response_model=Asset,
            methods=["POST"],
            tags=[tag],
            name=f"add_{entity_definition.name}_asset",
            description=f"Add an asset to {entity_definition.name}",
            endpoint=create_endpoint_wrapper(
                handler=add_asset,  # Replace with the actual handler for adding assets
                http_method="POST",
                path_params=path_params,
                include_body=False,
                upload_file=True,
                response_model=Asset,
                entity_definition=entity_definition,
                relation_collection=relation_collection,
                service=get_asset_service,
            ),
        )
