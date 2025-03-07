from enum import StrEnum as PyStrEnum


class AttributeType(PyStrEnum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    ENUM = "ENUM"
    GEOMETRY = "GEOMETRY"
