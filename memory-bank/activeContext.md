# activeContext.md

## Current Work
The project has been updated to support construction progress percentage tracking and prediction using a YOLO-based model. Key updates include:

- Dataset images are now organized in progress-labeled subfolders under `datasets/construction_raw_images/` (e.g., `10%/`, `15%/`, `20%/`, etc.).
- The dataset splitting script (`split_dataset.py`) reads images from these progress subfolders to create train/val/test splits.
- The annotation tool (`annotate.py`) has been enhanced to save progress metadata as comment lines in annotation files alongside bounding box labels.
- A custom dataset loader (`custom_dataset.py`) was created to load images, bounding boxes, and progress labels for multi-task training.
- The training script (`train.py`) was extended to add a regression head to the YOLO model for progress prediction and implements a custom training loop for joint detection and regression.
- The dataset configuration (`configs/dataset.yaml`) was updated to point to the new image directory structure.
- The dataset splitting logic in `split_dataset.py` was updated to preserve the progress percentage distributions by processing each progress group separately. The script shuffles, splits according to configured ratios, and copies images and labels into the appropriate output folders.

## Key Technical Concepts
- YOLO object detection model training using Ultralytics YOLOv8
- Dataset preparation in YOLO format (images + .txt annotations) with progress metadata
- Multi-task learning: object detection + progress regression
- Dataset YAML configuration for training, validation, and test splits
- GPU-accelerated training with batch size and image size configuration
- Annotation tool development using OpenCV for bounding box labeling and progress metadata
- Custom PyTorch dataset loader for progress-aware training
- Dataset splitting preserving progress percentage distribution

## Relevant Files and Code
- annotate.py: Annotation tool for labeling images with bounding boxes, class IDs, and progress metadata
- split_dataset.py: Dataset splitting script updated to handle progress-labeled subfolders and preserve distribution
- custom_dataset.py: Custom dataset loader for loading images, bounding boxes, and progress labels
- train.py: Training script extended for multi-task learning with progress regression
- configs/dataset.yaml: Dataset configuration updated for new directory structure

## Problem Solving
- Addressed lack of progress metadata in raw images by integrating progress labels in annotation files
- Designed and implemented progress metadata integration in annotation and dataset loading
- Extended model and training pipeline for progress prediction
- Refactored dataset splitting to group images by progress percentage and split each group separately to preserve distribution
- Ensured reproducibility with a random seed and maintained output directory structure and label copying

## Pending Tasks and Next Steps
- ✅ Fixed training script errors and successfully completed model training
- Model training completed for 100 epochs with simplified progress prediction model
- Trained model saved to `models/construction_progress.pt`
- Next steps: Evaluate model performance and implement full YOLO+progress regression if needed
- Consider implementing validation loop and model evaluation metrics
- Test the trained model on validation/test data
- Update memory bank files to document current progress and recent changes.

## Notes
- Annotation tool saves progress percentage as comment lines in annotation files.
- Tool supports deleting last bounding box, moving to next image, and quitting.
- Annotation files are saved in `datasets/labels/` with the same base name as images.
