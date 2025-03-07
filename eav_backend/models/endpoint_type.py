from enum import StrEnum as PyStrEnum


class EndpointType(PyStrEnum):
    LIST = "LIST"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
