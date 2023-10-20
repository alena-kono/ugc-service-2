import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleType(models.TextChoices):
    ACTOR = "actor", _("actor")
    WRITER = "writer", _("writer")
    DIRECTOR = "director", _("director")


class FilmType(models.TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv_show", _("tv_show")


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'content"."genre'
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        indexes = [
            models.Index(fields=["name"], name="genre_name_idx"),
        ]


class FilmWork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(_("title"))
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation_date"), blank=True, null=True)
    rating = models.FloatField(
        "rating",
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    type = models.TextField(choices=FilmType.choices)

    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")

    genres = models.ManyToManyField(Genre, through="GenreFilmwork")

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = "Кинопроизведение"
        verbose_name_plural = "Кинопроизведения"
        indexes = [
            models.Index(fields=["creation_date"], name="film_work_creation_date_idx"),
            models.Index(fields=["title"], name="film_work_title_idx"),
            models.Index(fields=["rating"], name="film_work_rating_idx"),
        ]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_("full_name"))

    film_work = models.ManyToManyField(FilmWork, through="PersonFilmWork")

    def __str__(self) -> str:
        return self.full_name

    class Meta:
        db_table = 'content"."person'
        verbose_name = "Актер"
        verbose_name_plural = "Актеры"
        indexes = [
            models.Index(fields=["full_name"], name="person_fullname_idx"),
        ]


class PersonFilmWork(UUIDMixin):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    role = models.TextField(_("role"), choices=RoleType.choices)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        constraints = [
            models.UniqueConstraint(
                fields=["film_work", "person", "role"],
                name="unique_person_role_per_film_idx",
            ),
        ]


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        constraints = [
            models.UniqueConstraint(
                fields=["film_work", "genre"], name="unique_film_work_genre_idx"
            ),
        ]
