from pydantic import BaseModel


class MetaInfoParam(BaseModel):
    title: str = ""
    description: str = ""


class SortBy(MetaInfoParam):
    title: str = "Field name"
    description: str = "Field name to sort by"


class OrderBy(MetaInfoParam):
    title: str = "Order direction"
    description: str = "Order direction to sort by"


class PageNumber(MetaInfoParam):
    title: str = "Number of the page"
    description: str = "Number of page to return when paginating"


class PageSize(MetaInfoParam):
    title: str = "Page size"
    description: str = "Number of records returned per page when paginating"


class FilterBy(MetaInfoParam):
    title: str = "Field name to be filtered by"
    description: str = "Name of field to be filtered by"


class FilterValue(MetaInfoParam):
    title: str = "Field value to be filtered by"
    description: str = "Value of field to be used for as a filter query"


class SearchQuery(MetaInfoParam):
    title: str = "Full text search query"
    description: str = "Query string for the items to search"


class DefaultMetaInfo(BaseModel):
    sort_by: SortBy = SortBy()
    order_by: OrderBy = OrderBy()
    page_number: PageNumber = PageNumber()
    page_size: PageSize = PageSize()
    filter_by: FilterBy = FilterBy()
    filter_value: FilterValue = FilterValue()
    search_query: SearchQuery = SearchQuery()
