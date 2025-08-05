import pathlib
import random
import shutil
import logging
import yaml
from typing import List

def split_dataset(config_path: str) -> None:
    """
    Split dataset into train, val, and test sets based on configuration.

    Args:
        config_path (str): Path to YAML configuration file.
    """
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    images_dir = pathlib.Path(config['images_dir'])
    labels_dir = pathlib.Path(config['labels_dir'])
    output_dir = pathlib.Path(config['output_dir'])
    train_ratio = config['train_ratio']
    val_ratio = config['val_ratio']
    test_ratio = config['test_ratio']
    seed = config['seed']

    # Validate ratios sum to 1.0
    total_ratio = train_ratio + val_ratio + test_ratio
    if not abs(total_ratio - 1.0) < 1e-6:
        logging.error(f"Train, val, test ratios must sum to 1.0. Current sum: {total_ratio}")
        return

    random.seed(seed)

    images = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
    if not images:
        logging.error(f"No images found in {images_dir}")
        return

    random.shuffle(images)

    total = len(images)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    test_count = total - train_count - val_count

    splits = {
        "train": images[:train_count],
        "val": images[train_count:train_count + val_count],
        "test": images[train_count + val_count:]
    }

    for split in splits:
        (output_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (output_dir / split / "labels").mkdir(parents=True, exist_ok=True)

    for split, files in splits.items():
        for img_path in files:
            dst_img_path = output_dir / split / "images" / img_path.name
            shutil.copy2(img_path, dst_img_path)

            label_path = labels_dir / (img_path.stem + ".txt")
            dst_label_path = output_dir / split / "labels" / (img_path.stem + ".txt")
            if label_path.exists():
                shutil.copy2(label_path, dst_label_path)

    logging.info(f"Dataset split completed:")
    logging.info(f"  Train: {len(splits['train'])} images")
    logging.info(f"  Val: {len(splits['val'])} images")
    logging.info(f"  Test: {len(splits['test'])} images")

if __name__ == "__main__":
    split_dataset("configs/dataset.yaml")
