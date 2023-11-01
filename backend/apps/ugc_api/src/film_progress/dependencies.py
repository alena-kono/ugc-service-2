from typing import Annotated

from fastapi import Depends
from src.film_progress.services import IFilmProgressService, get_service

FilmServiceType = Annotated[IFilmProgressService, Depends(get_service)]
