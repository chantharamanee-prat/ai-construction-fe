from typing import List
from models.box import Box
from pydantic import BaseModel

class Annotation(BaseModel):
    imageName: str
    progress: float  # 0-100
    boxes: List[Box]