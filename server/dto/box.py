from pydantic import BaseModel

class Box(BaseModel):
    classId: int
    xCenter: float
    yCenter: float
    width: float
    height: float