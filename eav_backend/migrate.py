import logging

from alembic import command
from alembic.config import Config


def run_migrations(
    schemas: list[str],
    connection_string: str,
    script_location: str = "./alembic",
    alembic_file: str = "./alembic.ini",
) -> None:
    for schema in schemas:
        logging.info(f"Running DB migrations in {script_location} on schema {schema}")
        alembic_cfg = get_alembic_config(
            connection_string=connection_string,
            schema=schema,
            script_location=script_location,
            alembic_file=alembic_file,
        )
        command.upgrade(alembic_cfg, "head")


def get_alembic_config(
    schema: str,
    connection_string: str,
    script_location: str = "./alembic",
    alembic_file: str = "./alembic.ini",
):
    alembic_cfg = Config(file_=alembic_file)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", connection_string)
    alembic_cfg.set_main_option("database.schema", schema)
    return alembic_cfg
