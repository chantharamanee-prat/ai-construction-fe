# activeContext.md

## Current Work
The project has been updated to support construction progress percentage tracking and prediction using a YOLO-based model. Key updates include:

- Dataset images are now organized in progress-labeled subfolders under `datasets/construction_raw_images/` (e.g., `10%/`, `15%/`, `20%/`, etc.).
- The dataset splitting script (`split_dataset.py`) reads images from these progress subfolders to create train/val/test splits.
- The annotation tool (`annotate.py`) has been enhanced to save progress metadata as comment lines in annotation files alongside bounding box labels.
- A custom dataset loader (`custom_dataset.py`) was created to load images, bounding boxes, and progress labels for multi-task training.
- The training script (`train.py`) was extended to add a regression head to the YOLO model for progress prediction and implements a custom training loop for joint detection and regression.
- The dataset configuration (`configs/dataset.yaml`) was updated to point to the new image directory structure.

## Key Technical Concepts
- YOLO object detection model training using Ultralytics YOLOv8
- Dataset preparation in YOLO format (images + .txt annotations) with progress metadata
- Multi-task learning: object detection + progress regression
- Dataset YAML configuration for training, validation, and test splits
- GPU-accelerated training with batch size and image size configuration
- Annotation tool development using OpenCV for bounding box labeling and progress metadata
- Custom PyTorch dataset loader for progress-aware training

## Relevant Files and Code
- annotate.py: Annotation tool for labeling images with bounding boxes, class IDs, and progress metadata
- split_dataset.py: Dataset splitting script updated to handle progress-labeled subfolders
- custom_dataset.py: Custom dataset loader for loading images, bounding boxes, and progress labels
- train.py: Training script extended for multi-task learning with progress regression
- configs/dataset.yaml: Dataset configuration updated for new directory structure

## Problem Solving
- Addressed lack of progress metadata in raw images by integrating progress labels in annotation files
- Designed and implemented progress metadata integration in annotation and dataset loading
- Extended model and training pipeline for progress prediction

## Pending Tasks and Next Steps
- Update memory bank documentation files to reflect new project conventions and technical changes
- Document the new dataset structure, annotation format, and training pipeline enhancements
- Ensure memory bank files like `activeContext.md`, `progress.md`, and `systemPatterns.md` capture these updates accurately
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
- Split annotated dataset into train/val/test sets using split_dataset.py
- Verify annotation quality
- Execute training by running train.py with updated model path in `models/` directory

## Notes
- Dataset is now properly organized for YOLO training
- Annotation tool expects images in `datasets/raw_images`
- Labels will be saved to `datasets/labels/`
- Model files are now stored and loaded from the `models/` directory, including pretrained and trained weights

## Recent Refactoring
- Refactored annotation tool to use YAML configuration, pathlib, logging, and type hints
- Refactored dataset splitting script to use YAML config, pathlib, logging, and input validation
- Refactored training script to externalize parameters, add logging, and use YAML config
- Updated project to follow PEP8, Google-style docstrings, and DEBUG logging level
- Added configuration files for annotation, dataset splitting, and training
