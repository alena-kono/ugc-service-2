# from django.contrib.postgres.aggregates import ArrayAgg
# from django.db.models import Q
from django.core.paginator import Page, Paginator
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.api.v1.logic import get_film_movies_queryset


class MoviesJSONMixin:
    http_method_names = ["get"]
    queryset = get_film_movies_queryset()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesJSONMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        original_context = super().get_context_data(object_list=None, **kwargs)

        paginator: Paginator = original_context["paginator"]
        page: Page = original_context["page_obj"]

        context = {
            "count": paginator.count,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "total_pages": paginator.num_pages,
            "results": list(original_context["object_list"]),
        }
        return context


class MoviesDetailApi(MoviesJSONMixin, BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        original_context = super().get_context_data(object_list=None, **kwargs)
        film_work = original_context["object"]
        return film_work
