from enum import Enum
from typing import Annotated, Any

from fastapi import Query
from src.common.dependencies import (
    META_INFO,
    CommonOrderByParams,
    FilterRequestParams,
    FullTextSearchParams,
    PaginationRequestParams,
    SortRequestParams,
)


class FilmSortOptions(str, Enum):
    IMDB: str = "imdb_rating"


class FilmFilterOptions(str, Enum):
    GENRE_ID: str = "genre_id"


class FilmRequestParams(
    SortRequestParams,
    PaginationRequestParams,
    FilterRequestParams,
    FullTextSearchParams,
):
    SORT_ES_MAPPING = {FilmSortOptions.IMDB: FilmSortOptions.IMDB.value}

    sort_by: Annotated[
        FilmSortOptions,
        Query(
            title=META_INFO.sort_by.title,
            description=META_INFO.sort_by.description,
        ),
    ] = FilmSortOptions.IMDB
    order_by: Annotated[
        CommonOrderByParams,
        Query(
            title=META_INFO.order_by.title,
            description=META_INFO.order_by.description,
        ),
    ] = CommonOrderByParams.DESC

    filter_by: Annotated[
        FilmFilterOptions | None,
        Query(
            title=META_INFO.filter_by.title,
            description=META_INFO.filter_by.description,
        ),
    ] = None

    def to_es_params(self) -> dict[str, Any]:
        pagination_params = PaginationRequestParams.to_es_params(self)
        sort_params = SortRequestParams.to_es_params(self)
        full_text_params = FullTextSearchParams.to_es_params(self)
        filter_params = FilterRequestParams.to_es_params(self)

        params = {**pagination_params, **sort_params}
        if full_text_params or filter_params:
            params["query"] = {"bool": {**full_text_params, **filter_params}}
        return params

    def es_filter_by_genre_id(self) -> dict[str, Any]:
        filter_subquery = {
            "filter": {
                "nested": {
                    "path": "genres",
                    "query": {"term": {"genres.id": self.filter_value}},
                }
            },
        }
        return filter_subquery
