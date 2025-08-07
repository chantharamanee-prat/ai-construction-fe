import os
from pathlib import Path
from ultralytics import YOLO
import tempfile

from fastapi import HTTPException

def predict_image_yolo(model_path: str, file_bytes: bytes, file_suffix: str):
    """Run YOLO model prediction on image bytes."""
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Load YOLO model
        model = YOLO(model_path)
        results = model.predict(tmp_path)

        # Define class names mapping for construction progress classification
        class_names = {
            0: "10%",
            1: "15%", 
            2: "20%",
            3: "25%",
            4: "30%",
            5: "40%",
            6: "50%"
        }

        # Parse results (classification or detection)
        predictions = []
        for r in results:
            if hasattr(r, 'probs') and r.probs is not None:
                # For classification
                top_indices = r.probs.top5
                top_scores = r.probs.top5conf
                for idx, score in zip(top_indices, top_scores):
                    class_name = class_names.get(int(idx), f"Class_{int(idx)}")
                    predictions.append({
                        "class": class_name,
                        "confidence": float(score)
                    })
            elif hasattr(r, 'boxes') and r.boxes is not None:
                # For detection
                for box in r.boxes:
                    class_name = class_names.get(int(box.cls[0]), f"Class_{int(box.cls[0])}")
                    predictions.append({
                        "class": class_name,
                        "confidence": float(box.conf[0]),
                        "box": [float(x) for x in box.xyxy[0].tolist()]
                    })

        # Clean up temp file
        os.remove(tmp_path)

        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


