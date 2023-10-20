from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmwork, Person, PersonFilmWork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ("genre", "film_work")


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ("person", "film_work")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,)
    search_fields = ("name",)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmWorkInline)

    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
    )
    list_filter = (
        "title",
        "type",
        "creation_date",
    )
    search_fields = (
        "title",
        "description",
        "id",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmWorkInline,)

    list_display = (
        "full_name",
        "id",
    )
    search_fields = ("full_name",)
