from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet
from movies.models import FilmWork, RoleType


def get_film_movies_queryset() -> QuerySet[FilmWork]:
    return (
        FilmWork.objects.values(
            "id", "title", "description", "creation_date", "rating", "type"
        )
        .annotate(
            genres=ArrayAgg("genres__name", distinct=True),
            actors=ArrayAgg(
                "person__full_name",
                distinct=True,
                filter=Q(personfilmwork__role=RoleType.ACTOR),
            ),
            writers=ArrayAgg(
                "person__full_name",
                distinct=True,
                filter=Q(personfilmwork__role=RoleType.WRITER),
            ),
            directors=ArrayAgg(
                "person__full_name",
                distinct=True,
                filter=Q(personfilmwork__role=RoleType.DIRECTOR),
            ),
        )
        .order_by("id")
    )
