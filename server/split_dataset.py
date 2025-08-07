import pathlib
import random
import shutil
import logging
import yaml

def split_dataset(config_path: str) -> None:
    """
    Split dataset into train, val, and test sets based on configuration,
    supporting both classification and detection datasets.

    Args:
        config_path (str): Path to YAML configuration file.
    """
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    images_root_dir = pathlib.Path(config['images_dir'])
    base_output_dir = pathlib.Path(config['output_dir'])
    train_ratio = config['train_ratio']
    val_ratio = config['val_ratio']
    test_ratio = config['test_ratio']
    seed = config['seed']
    dataset_type = config.get('dataset_type', 'detection')  # 'classification' or 'detection'

    # Choose split output folder based on dataset_type
    if dataset_type == 'classification':
        output_dir = base_output_dir.parent / 'split_classification'
    else:
        output_dir = base_output_dir.parent / 'split_detection'

    # Validate ratios sum to 1.0
    total_ratio = train_ratio + val_ratio + test_ratio
    if not abs(total_ratio - 1.0) < 1e-6:
        logging.error(f"Train, val, test ratios must sum to 1.0. Current sum: {total_ratio}")
        return

    random.seed(seed)

    if dataset_type == 'classification':
        split_classification_dataset(images_root_dir, output_dir, train_ratio, val_ratio, test_ratio)
    else:
        split_detection_dataset(config, images_root_dir, output_dir, train_ratio, val_ratio, test_ratio)

def split_classification_dataset(images_root_dir, output_dir, train_ratio, val_ratio, test_ratio):
    """Split classification dataset where each folder represents a class."""
    
    # Collect images grouped by class (folder names)
    class_groups = {}
    for class_dir in images_root_dir.iterdir():
        if class_dir.is_dir():
            class_name = class_dir.name
            class_images = []
            for img_path in class_dir.iterdir():
                if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
                    class_images.append(img_path)
            if class_images:
                class_groups[class_name] = class_images
                logging.info(f"Found {len(class_images)} images in class '{class_name}'")

    if not class_groups:
        logging.error(f"No images found in {images_root_dir} with class subfolders")
        return

    splits = {"train": [], "val": []}
    if test_ratio > 0:
        splits["test"] = []

    # Split each class separately to maintain class distribution
    for class_name, images in class_groups.items():
        random.shuffle(images)
        total = len(images)
        train_count = int(total * train_ratio)
        val_count = int(total * val_ratio)
        test_count = total - train_count - val_count if test_ratio > 0 else 0

        splits["train"].extend([(img, class_name) for img in images[:train_count]])
        splits["val"].extend([(img, class_name) for img in images[train_count:train_count + val_count]])
        if test_ratio > 0:
            splits["test"].extend([(img, class_name) for img in images[train_count + val_count:]])

        logging.info(f"Class '{class_name}': Train={train_count}, Val={val_count}, Test={test_count}")

    # Create output directories for classification
    for split in splits:
        for class_name in class_groups.keys():
            (output_dir / split / class_name).mkdir(parents=True, exist_ok=True)

    # Copy images to respective class directories
    for split, files in splits.items():
        for img_path, class_name in files:
            dst_img_path = output_dir / split / class_name / img_path.name
            shutil.copy2(img_path, dst_img_path)

    logging.info(f"Classification dataset split completed:")
    logging.info(f"  Train: {len(splits['train'])} images")
    logging.info(f"  Val: {len(splits['val'])} images")
    if "test" in splits:
        logging.info(f"  Test: {len(splits['test'])} images")

def split_detection_dataset(config, images_root_dir, output_dir, train_ratio, val_ratio, test_ratio):
    """Split detection dataset with images and corresponding label files."""
    
    labels_dir = pathlib.Path(config['labels_dir'])
    
    # Collect images grouped by progress percentage from subfolder names
    progress_groups = {}
    for progress_dir in images_root_dir.iterdir():
        if progress_dir.is_dir():
            try:
                progress_percent = int(progress_dir.name.rstrip('%'))
            except ValueError:
                logging.warning(f"Skipping folder with invalid progress name: {progress_dir.name}")
                continue
            group_images = []
            for img_path in progress_dir.iterdir():
                if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                    group_images.append(img_path)
            if group_images:
                progress_groups[progress_percent] = group_images

    if not progress_groups:
        logging.error(f"No images found in {images_root_dir} with progress subfolders")
        return

    splits = {"train": [], "val": []}
    if test_ratio > 0:
        splits["test"] = []

    # Split each progress group separately and combine
    for progress, images in progress_groups.items():
        random.shuffle(images)
        total = len(images)
        train_count = int(total * train_ratio)
        val_count = int(total * val_ratio)
        test_count = total - train_count - val_count if test_ratio > 0 else 0

        splits["train"].extend([(img, progress) for img in images[:train_count]])
        splits["val"].extend([(img, progress) for img in images[train_count:train_count + val_count]])
        if test_ratio > 0:
            splits["test"].extend([(img, progress) for img in images[train_count + val_count:]])

    # Create output directories
    for split in splits:
        (output_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (output_dir / split / "labels").mkdir(parents=True, exist_ok=True)

    # Copy images and labels to respective directories
    for split, files in splits.items():
        for img_path, progress in files:
            dst_img_path = output_dir / split / "images" / img_path.name
            shutil.copy2(img_path, dst_img_path)

            label_path = labels_dir / (img_path.stem + ".txt")
            dst_label_path = output_dir / split / "labels" / (img_path.stem + ".txt")
            if label_path.exists():
                shutil.copy2(label_path, dst_label_path)

    logging.info(f"Detection dataset split completed:")
    logging.info(f"  Train: {len(splits['train'])} images")
    logging.info(f"  Val: {len(splits['val'])} images")
    if "test" in splits:
        logging.info(f"  Test: {len(splits['test'])} images")

if __name__ == "__main__":
    split_dataset("configs/dataset.yaml")