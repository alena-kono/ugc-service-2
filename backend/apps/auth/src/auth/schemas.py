from src.auth.jwt import schemas as jwt_schemas
from src.common import schemas as common_schemas
from src.users import schemas as users_schemas


class AuthenticatedUser(common_schemas.AppBaseSchema):
    credentials: jwt_schemas.JWTCredentials
    user: users_schemas.User
