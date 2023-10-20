import http
import logging
from enum import Enum
from typing import Annotated, Any, Callable, ClassVar, Coroutine

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from src.common.authorization import JWTBearer
from src.common.meta_info import DefaultMetaInfo
from src.common.repository import RepositoryType
from src.common.schemas import JwtClaims
from src.settings.app import AppSettings

logger = logging.getLogger("root")

settings = AppSettings.get()

META_INFO = DefaultMetaInfo()

UserToken = Annotated[JwtClaims, Depends(JWTBearer())]


class CommonOrderByParams(str, Enum):
    ASC: str = "asc"
    DESC: str = "desc"


class RequestParams(BaseModel):
    def to_db_params(self, db_type: RepositoryType) -> dict[str, Any]:
        if db_type == RepositoryType.ES:
            return self.to_es_params()
        raise NotImplementedError

    def to_es_params(self) -> dict[str, Any]:
        raise NotImplementedError


class SortRequestParams(RequestParams):
    SORT_ES_MAPPING: ClassVar[dict]

    sort_by: Annotated[
        Enum | None,
        Query(
            title=META_INFO.sort_by.title,
            description=META_INFO.sort_by.description,
        ),
    ] = None
    order_by: Annotated[
        CommonOrderByParams,
        Query(
            title=META_INFO.order_by.title,
            description=META_INFO.order_by.description,
        ),
    ] = CommonOrderByParams.ASC

    def to_es_params(self) -> dict[str, Any]:
        return {"sort": {self.SORT_ES_MAPPING[self.sort_by]: self.order_by.value}}


class PaginationRequestParams(RequestParams):
    page_number: int = Field(
        default=Query(
            default=1,
            title=META_INFO.page_number.title,
            description=META_INFO.page_number.description,
            ge=1,
        )
    )
    page_size: int = Field(
        Query(
            default=settings.service.default_page_size,
            title=META_INFO.page_size.title,
            description=META_INFO.page_size.description,
            ge=1,
            le=settings.elastic.max_docs_to_fetch_at_one_time,
        ),
    )

    def to_es_params(self) -> dict[str, Any]:
        return {"from": (self.page_number - 1) * self.page_size, "size": self.page_size}


class FilterRequestParams(RequestParams):
    filter_by: Annotated[
        Enum | None,
        Query(
            title=META_INFO.filter_by.title,
            description=META_INFO.filter_by.description,
        ),
    ] = None
    filter_value: Annotated[
        str | None,
        Query(
            title=META_INFO.filter_value.title,
            description=META_INFO.filter_value.description,
        ),
    ] = None

    def to_es_params(self) -> dict[str, Any]:
        if self.filter_by:
            func = getattr(self, f"es_filter_by_{self.filter_by.value}")
            return func()
        return {}


class FullTextSearchParams(RequestParams):
    query: Annotated[
        str | None,
        Query(
            title=META_INFO.search_query.title,
            description=META_INFO.search_query.description,
        ),
    ] = None

    def to_es_params(self) -> dict[str, Any]:
        if self.query:
            return {"must": {"query_string": {"query": self.query}}}
        return {}


CheckPermissionType = Callable[[UserToken], Coroutine[None, None, JwtClaims]]


def check_permission(permission_name: str) -> CheckPermissionType:
    async def _check_permission(user_token: UserToken) -> JwtClaims:
        if permission_name not in user_token.user.permissions:
            logger.exception(
                f"User {user_token.user.id} does not have a {permission_name=}. Users permissions are {user_token.user.permissions}."
            )
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="User does not have a permission to perform this action.",
            )

        return user_token

    return _check_permission
