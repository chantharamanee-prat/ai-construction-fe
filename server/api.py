from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import List
import os
from pathlib import Path

from api_handlers.image_loader import list_images, get_image_path
from api_handlers.annotation_handler import save_annotation_to_file
from dto.annotation import Annotation
from dto.image import ImageDTO, DatasetDTO

app = FastAPI()

# CORS middleware (no restrictions as per user)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "datasets" / "raw_images"
LABELS_DIR = BASE_DIR / "datasets" / "labels"


@app.get("/api/datasets", response_model=List[DatasetDTO])
async def get_datasets():
    datasets = []
    for dataset_dir in DATASET_DIR.iterdir():
        if dataset_dir.is_dir():
            image_count = 0
            annotated_count = 0

            
            for image_path in list_images(dataset_dir):
                image_count += 1
                label_path = LABELS_DIR / Path(image_path).with_suffix(".txt").name
                if label_path.exists():
                    annotated_count += 1
            
            progress = dataset_dir.name.replace("%", "")
            datasets.append(DatasetDTO(
                name=dataset_dir.name,
                image_count=image_count,
                annotated_count=annotated_count,
                progress=progress
            ))
    return datasets

@app.get("/api/images", response_model=List[ImageDTO])
async def get_images():
    images = []
    for image_path in list_images(DATASET_DIR):
        label_path = LABELS_DIR / Path(image_path).with_suffix(".txt").name
        annotated = label_path.exists()
        progress = 0.0
        if annotated:
            try:
                with open(label_path, "r") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# progress:"):
                        progress = float(first_line.split(":")[1].strip())
            except:
                pass
        images.append(ImageDTO(
            path=image_path,
            annotated=annotated,
            progress=progress
        ))
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
