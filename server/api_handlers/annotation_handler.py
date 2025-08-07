from pathlib import Path
from typing import List
from dto.annotation import Annotation 
from .image_loader import list_images, get_image_path

def save_annotation_to_file(labels_dir: Path, annotation: Annotation) -> None:
    """
    Save annotation data to YOLO format file with progress comment.
    The annotation.imageName is the image filename with possible subdirectory.
    The label file is saved as labels_dir/{image_basename}.txt
    """
    # Ensure labels directory exists
    labels_dir.mkdir(parents=True, exist_ok=True)

    # Extract base filename without extension for label file
    image_path = Path(annotation.imageName)
    label_filename = image_path.with_suffix(".txt").name
    label_path = labels_dir / label_filename

    # Prepare lines to write
    lines = []
    # Progress comment line
    # lines.append(f"# progress: {annotation.progress}")

    # Each box line: classId xCenter yCenter width height (floats formatted to 6 decimals)
    for box in annotation.boxes:
        line = f"{box.classId} {box.xCenter:.6f} {box.yCenter:.6f} {box.width:.6f} {box.height:.6f}"
        lines.append(line)

    # Write to file
    with open(label_path, "w") as f:
        f.write("\n".join(lines) + "\n")
