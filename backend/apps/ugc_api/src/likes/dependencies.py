from typing import Annotated

from fastapi import Depends
from src.likes.services import ILikeService, get_service

LikeServiceType = Annotated[ILikeService, Depends(get_service)]
