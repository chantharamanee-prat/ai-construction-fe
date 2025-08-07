from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote

from typing import List
import os
from pathlib import Path

from api_handlers.image_loader import list_images, get_image_path
from api_handlers.annotation_handler import save_annotation_to_file
from dto.annotation import Annotation
from dto.image import ImageDTO, DatasetDTO, BoxDTO, AnnotatedImageDTO

# YOLO import
import tempfile
from api_handlers.ml_handler import predict_image_yolo

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


@app.get("/api/images/{image_path:path}")
async def serve_image(image_path: str):
    full_path = get_image_path(DATASET_DIR, image_path)
    if not full_path or not full_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(full_path)

@app.get("/api/datasets/{dataset_name}", response_model=List[AnnotatedImageDTO])
async def get_dataset_images(dataset_name: str):
    """Get all images in a specific dataset directory with their annotations"""
    decoded_name = unquote(dataset_name)
    dataset_path = DATASET_DIR / decoded_name
    
    if not dataset_path.exists() or not dataset_path.is_dir():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    images = []
    for image_path in list_images(dataset_path):
        label_path = LABELS_DIR / Path(image_path).with_suffix(".txt").name
        annotated = label_path.exists()
        progress = 0.0
        
        boxes = []
        if annotated:
            try:
                with open(label_path, "r") as f:
                    lines = f.readlines()
                    if lines and lines[0].startswith("# progress:"):
                        progress = float(lines[0].split(":")[1].strip())
                    for line in lines[1:]:
                        if line.strip():
                            parts = line.split()
                            boxes.append(BoxDTO(
                                classId=int(parts[0]),
                                xCenter=float(parts[1]),
                                yCenter=float(parts[2]),
                                width=float(parts[3]),
                                height=float(parts[4])
                            ))
            except Exception as e:
                print(f"Error parsing annotation {label_path}: {e}")
        
        images.append(AnnotatedImageDTO(
            path=str( "/{0}/{1}".format(dataset_name, image_path)),
            annotated=annotated,
            progress=progress,
            boxes=boxes
        ))
    
    return images

@app.post("/api/annotations", status_code=201)
async def save_annotation(annotation: Annotation):
    try:
        save_annotation_to_file(LABELS_DIR, annotation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Annotation saved successfully"}


@app.post("/api/predict")
async def predict_image(file: UploadFile = File(...)):
    """Run YOLO model prediction on an uploaded image."""
    file_bytes = await file.read()
    model_path = str(BASE_DIR / "models" / "progress-classification.pt")
    predictions = predict_image_yolo(model_path, file_bytes, Path(file.filename).suffix)
    return {"predictions": predictions}
