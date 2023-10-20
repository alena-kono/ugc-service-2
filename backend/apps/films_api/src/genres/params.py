from enum import Enum
from typing import Annotated, Any

from fastapi import Query
from src.common.dependencies import (
    META_INFO,
    FullTextSearchParams,
    PaginationRequestParams,
    SortRequestParams,
)


class GenreSortOptions(str, Enum):
    NAME: str = "name"


class GenreRequestParams(
    SortRequestParams, PaginationRequestParams, FullTextSearchParams
):
    SORT_ES_MAPPING = {GenreSortOptions.NAME: f"{GenreSortOptions.NAME.value}.raw"}

    sort_by: Annotated[
        GenreSortOptions,
        Query(
            title=META_INFO.sort_by.title,
            description=META_INFO.sort_by.description,
        ),
    ] = GenreSortOptions.NAME

    def to_es_params(self) -> dict[str, Any]:
        pagination_params = PaginationRequestParams.to_es_params(self)
        sort_params = SortRequestParams.to_es_params(self)
        full_text_params = FullTextSearchParams.to_es_params(self)

        params = {**pagination_params, **sort_params}
        if full_text_params:
            params["query"] = {
                "bool": {
                    **full_text_params,
                }
            }
        return params
