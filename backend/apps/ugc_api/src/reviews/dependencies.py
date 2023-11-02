from typing import Annotated

from fastapi import Depends
from src.reviews.services import IReviewService, get_service

ReviewServiceType = Annotated[IReviewService, Depends(get_service)]
