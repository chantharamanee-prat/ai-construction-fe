from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import List
import os
from pathlib import Path

from handlers.image_loader import list_images, get_image_path
from handlers.annotation_handler import save_annotation_to_file
from models.annotation import Annotation

app = FastAPI()

# CORS middleware (no restrictions as per user)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASET_DIR = Path("datasets/construction_raw_images")
LABELS_DIR = Path("datasets/labels")


@app.get("/api/images", response_model=List[str])
async def get_images():
    images = list_images(DATASET_DIR)
    return images

@app.get("/api/images/{image_path:path}")
async def serve_image(image_path: str):
    full_path = get_image_path(DATASET_DIR, image_path)
    if not full_path or not full_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(full_path)

@app.post("/api/annotations", status_code=201)
async def save_annotation(annotation: Annotation):
    try:
        save_annotation_to_file(LABELS_DIR, annotation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Annotation saved successfully"}
