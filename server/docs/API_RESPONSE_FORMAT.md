# API Response Format

## Prediction Endpoint: `/api/predict`

### Response Structure

```json
{
  "predictions": {
    "classification": [
      {
        "class": "25%",
        "confidence": 0.8542
      },
      {
        "class": "30%",
        "confidence": 0.1234
      }
    ],
    "detection": [
      {
        "class": "25%",
        "confidence": 0.7234,
        "bbox": {
          "x1": 120.5,
          "y1": 80.2,
          "x2": 300.8,
          "y2": 250.6
        },
        "center": {
          "x": 210.65,
          "y": 165.4
        },
        "dimensions": {
          "width": 180.3,
          "height": 170.4
        }
      }
    ],
    "overall_progress": "25%",
    "progress_confidence": 0.8542
  }
}
```

### Field Descriptions

#### Classification Results

- `classification`: Array of classification predictions sorted by confidence (highest first)
  - `class`: Progress percentage (10%, 15%, 20%, 25%, 30%, 40%, 50%)
  - `confidence`: Confidence score (0.0 - 1.0)

#### Detection Results

- `detection`: Array of detected objects with bounding boxes
  - `class`: Progress percentage detected in the object
  - `confidence`: Detection confidence score (0.0 - 1.0)
  - `bbox`: Bounding box coordinates
    - `x1`, `y1`: Top-left corner
    - `x2`, `y2`: Bottom-right corner
  - `center`: Center point of bounding box
    - `x`, `y`: Center coordinates
  - `dimensions`: Box dimensions
    - `width`, `height`: Box width and height

#### Overall Results

- `overall_progress`: The most confident progress prediction from classification
- `progress_confidence`: Confidence score of the overall progress prediction

### Usage for Frontend

```javascript
// Example usage in frontend
const response = await fetch("/api/predict", {
  method: "POST",
  body: formData,
});

const data = await response.json();
const predictions = data.predictions;

// Get overall progress
const progress = predictions.overall_progress; // "25%"
const confidence = predictions.progress_confidence; // 0.8542

// Get all classification results
const allClassifications = predictions.classification;

// Get detection results with bounding boxes
const detections = predictions.detection;

// Draw bounding boxes
detections.forEach((detection) => {
  const bbox = detection.bbox;
  // Draw rectangle from (x1, y1) to (x2, y2)
  drawRectangle(bbox.x1, bbox.y1, bbox.x2, bbox.y2);
});
```

### Error Handling

If either model fails to load or predict, the corresponding array will be empty but the request will still succeed with available results.

Example with classification failure:

```json
{
  "predictions": {
    "classification": [],
    "detection": [...],
    "overall_progress": null,
    "progress_confidence": 0.0
  }
}
```
