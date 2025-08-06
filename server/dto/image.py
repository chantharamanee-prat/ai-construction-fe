from pydantic import BaseModel
from typing import List

class ImageDTO(BaseModel):
    path: str
    annotated: bool
    progress: float = 0.0  # Default to 0 if not annotated

class DatasetDTO(BaseModel):
    name: str
    image_count: int
    annotated_count: int
    progress: float
