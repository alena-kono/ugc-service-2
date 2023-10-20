from pydantic import BaseModel, Field


class PermissionCreate(BaseModel):
    name: str = Field(min_length=3)


class PermissionUpdate(BaseModel):
    name: str = Field(min_length=3)
