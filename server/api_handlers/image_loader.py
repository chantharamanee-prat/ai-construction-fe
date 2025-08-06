import os
from pathlib import Path
from typing import List

def list_images(dataset_dir: Path) -> List[str]:
    """
    Recursively list all image files in dataset_dir.
    Returns list of relative paths as strings with forward slashes.
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    images = []
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                full_path = Path(root) / file
                relative_path = full_path.relative_to(dataset_dir)
                images.append(str(relative_path).replace(os.sep, "/"))
    return images

def get_image_path(dataset_dir: Path, image_path: str) -> Path:
    """
    Given a relative image_path, return the full Path object if exists, else None.
    """
    full_path = dataset_dir / image_path
    if full_path.exists() and full_path.is_file():
        return full_path
    return None
