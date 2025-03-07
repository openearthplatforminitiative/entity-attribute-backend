from pydantic import ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    version: str = "0.0.1"
    uvicorn_port: int = 8080
    uvicorn_host: str = "0.0.0.0"
    uvicorn_reload: bool = True
    uvicorn_proxy_headers: bool = False
    api_root_path: str = ""
    api_description: str = ""
    api_domain: str = "localhost"

    log_level: str = "INFO"

    postgres_user: str = "eav_user"
    postgres_password: str = "eav_pass"
    postgres_db: str = "eav"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_schema: str = "public"

    run_migrations: bool = True
    alembic_directory: str = "./alembic"
    alembic_file: str = "./alembic.ini"

    import_entities: bool = True
    update_entities: bool = False
    import_config: str | None = None

    enable_admin_api: bool = False
    enable_metrics: bool = False

    @property
    def api_url(self):
        if self.api_domain == "localhost":
            return f"http://{self.api_domain}:{self.uvicorn_port}"
        else:
            return f"https://{self.api_domain}{self.api_root_path}"

    @property
    def database_connection(self):
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?options=-csearch_path={self.postgres_schema}"

    @property
    def logging_config(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "detailed",
                },
            },
            "loggers": {
                "openepi": {
                    "level": self.log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }


try:
    settings = Settings()
except ValidationError as exception:
    print("Invalid settings")
