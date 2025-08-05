# activeContext.md

## Current Work
We have prepared the training setup for a YOLO model to monitor construction progress. The dataset has been reorganized with:
- All images moved to `datasets/raw_images/` (134 images)
- Created directory structure:
  ```
  datasets/
  ├── raw_images/      # All source images
  ├── labels/          # Annotation files
  ├── train/           # Training split (70%)
  │   ├── images/
  │   └── labels/
  ├── val/             # Validation split (20%)
  │   ├── images/
  │   └── labels/
  └── test/            # Test split (10%)
      ├── images/
      └── labels/
  ```

The annotation tool (annotate.py) is ready for labeling images with five classes: foundation, column, beam, roof, and wall. The dataset configuration (data.yaml) is properly set up for the new structure.

## Key Technical Concepts
- YOLO object detection model training using Ultralytics YOLOv8
- Dataset preparation in YOLO format (images + .txt annotations)
- Dataset YAML configuration for training, validation, and test splits
- GPU-accelerated training with batch size and image size configuration
- Annotation tool development using OpenCV for bounding box labeling

## Relevant Files and Code
- annotate.py: Annotation tool for labeling images with bounding boxes and class IDs
- data.yaml: Dataset configuration file specifying dataset splits and class names
- train.py: Training script to run YOLOv8n training with specified parameters

## Problem Solving
- Addressed directory structure mismatch (raw_image → raw_images)
- Flattened nested image directory structure
- Created proper train/val/test splits
- Prepared annotation workflow

## Pending Tasks and Next Steps
- Annotate all images using annotate.py
- Split annotated dataset into train/val/test sets
- Verify annotation quality
- Execute training by running train.py with updated model path in `models/` directory

## Notes
- Dataset is now properly organized for YOLO training
- Annotation tool expects images in `datasets/raw_images`
- Labels will be saved to `datasets/labels/`
- Model files are now stored and loaded from the `models/` directory, including pretrained and trained weights
