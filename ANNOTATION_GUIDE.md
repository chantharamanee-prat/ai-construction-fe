# Annotation Guide for Construction Progress Dataset

This guide explains how to annotate images using the provided annotation tool (`annotate.py`).

## Prerequisites
- Python environment with OpenCV installed
- Dataset images located in `datasets/raw_images/`
- Annotation tool script: `annotate.py`

## Annotation Workflow

1. Run the annotation tool:
   ```bash
   python annotate.py
   ```

2. For each image:
   - Draw bounding boxes around construction elements by clicking and dragging the mouse.
   - After releasing the mouse button, select the class ID for the bounding box from the terminal prompt:
     - 0: foundation
     - 1: column
     - 2: beam
     - 3: roof
     - 4: wall
     - 5: floor
   - The bounding box will be displayed on the image.
   - Use the following keyboard controls:
     - `n`: Save annotations and move to the next image
     - `d`: Delete the last bounding box drawn
     - `q`: Save annotations and quit the tool

3. Annotations are saved in YOLO format as `.txt` files in the `datasets/labels/` directory, with the same base filename as the image.

## Notes
- Ensure all relevant objects are annotated in each image.
- Take care to accurately draw bounding boxes around objects.
- The annotation process is manual and requires human input for class selection.

## After Annotation
- Once all images are annotated, run the dataset splitting script:
  ```bash
  python split_dataset.py
  ```
- This will create the train/val/test splits in the `datasets/` directory.

## Contact
For questions or issues, contact the project maintainer.
