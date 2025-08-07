from pydantic import BaseModel
from typing import List

class BoxDTO(BaseModel):
    classId: int
    xCenter: float
    yCenter: float
    width: float
    height: float

class ImageDTO(BaseModel):
    path: str
    annotated: bool
    progress: float = 0.0  # Default to 0 if not annotated

class AnnotatedImageDTO(ImageDTO):
    boxes: List[BoxDTO] = []

class DatasetDTO(BaseModel):
    name: str
    image_count: int
    annotated_count: int
    progress: float
