import os
from pathlib import Path
from ultralytics import YOLO
import tempfile

from fastapi import HTTPException

def predict_image_yolo(classification_model_path: str, detection_model_path: str, file_bytes: bytes, file_suffix: str):
    """Run YOLO model prediction on image bytes using both classification and detection models."""
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Define class names mapping for construction progress
        classification_class_names = {
            0: "10%",
            1: "15%", 
            2: "20%",
            3: "25%",
            4: "30%",
            5: "40%",
            6: "50%"
        }
        
        # Define class names mapping for detection (from detection.yaml)
        detection_class_names = {
            0: "foundation",
            1: "column",
            2: "beam",
            3: "roof",
            4: "wall",
            5: "floor"
        }

        # Initialize results structure
        result = {
            "classification": [],
            "detection": [],
            "overall_progress": None,
            "progress_confidence": 0.0
        }

        # Run classification model
        try:
            classification_model = YOLO(classification_model_path)
            classification_results = classification_model.predict(tmp_path)
            
            for r in classification_results:
                if hasattr(r, 'probs') and r.probs is not None:
                    # Get top 5 predictions for classification
                    top_indices = r.probs.top5
                    top_scores = r.probs.top5conf
                    for idx, score in zip(top_indices, top_scores):
                        class_name = classification_class_names.get(int(idx), f"Class_{int(idx)}")
                        result["classification"].append({
                            "class": class_name,
                            "confidence": float(score)
                        })
                    
                    # Set overall progress from the highest confidence classification
                    if result["classification"]:
                        result["overall_progress"] = result["classification"][0]["class"]
                        result["progress_confidence"] = result["classification"][0]["confidence"]
                        
        except Exception as e:
            print(f"Classification model error: {e}")
            result["classification"] = []

        # Run detection model
        try:
            detection_model = YOLO(detection_model_path)
            detection_results = detection_model.predict(tmp_path)
            
            for r in detection_results:
                if hasattr(r, 'boxes') and r.boxes is not None:
                    # Get all detected objects
                    for box in r.boxes:
                        class_name = detection_class_names.get(int(box.cls[0]), f"Class_{int(box.cls[0])}")
                        result["detection"].append({
                            "class": class_name,
                            "confidence": float(box.conf[0]),
                            "bbox": {
                                "x1": float(box.xyxy[0][0]),
                                "y1": float(box.xyxy[0][1]),
                                "x2": float(box.xyxy[0][2]),
                                "y2": float(box.xyxy[0][3])
                            },
                            "center": {
                                "x": float(box.xywh[0][0]),
                                "y": float(box.xywh[0][1])
                            },
                            "dimensions": {
                                "width": float(box.xywh[0][2]),
                                "height": float(box.xywh[0][3])
                            }
                        })
                        
        except Exception as e:
            print(f"Detection model error: {e}")
            result["detection"] = []

        # Clean up temp file
        os.remove(tmp_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


