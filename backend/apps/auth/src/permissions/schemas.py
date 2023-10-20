from src.common import schemas as common_schemas


class Permission(common_schemas.UUIDSchemaMixin, common_schemas.TimestampSchemaMixin):
    name: str
