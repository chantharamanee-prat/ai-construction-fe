import os
import random
import shutil

def split_dataset(
    images_dir="datasets/raw_images",
    labels_dir="datasets/labels",
    output_dir="datasets",
    train_ratio=0.7,
    val_ratio=0.2,
    test_ratio=0.1,
    seed=42
):
    random.seed(seed)

    # Get list of image files
    images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()

    # Shuffle images
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

    # Create output directories
    for split in splits:
        images_out_dir = os.path.join(output_dir, split, "images")
        labels_out_dir = os.path.join(output_dir, split, "labels")
        os.makedirs(images_out_dir, exist_ok=True)
        os.makedirs(labels_out_dir, exist_ok=True)

    # Copy files to respective directories
    for split, files in splits.items():
        for img_file in files:
            # Copy image
            src_img_path = os.path.join(images_dir, img_file)
            dst_img_path = os.path.join(output_dir, split, "images", img_file)
            shutil.copy2(src_img_path, dst_img_path)

            # Copy corresponding label file if exists
            base_name = os.path.splitext(img_file)[0]
            label_file = base_name + ".txt"
            src_label_path = os.path.join(labels_dir, label_file)
            dst_label_path = os.path.join(output_dir, split, "labels", label_file)
            if os.path.exists(src_label_path):
                shutil.copy2(src_label_path, dst_label_path)

    print(f"Dataset split completed:")
    print(f"  Train: {len(splits['train'])} images")
    print(f"  Val: {len(splits['val'])} images")
    print(f"  Test: {len(splits['test'])} images")

if __name__ == "__main__":
    split_dataset()
