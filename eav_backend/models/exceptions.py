from eav_backend.models import EntityDefinition


class EAVException(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    @property
    def detail(self):
        return [{"msg": self.msg}]


class ExistsException(EAVException):
    def __init__(self, msg: str):
        super().__init__(msg)
