import os
from pathlib import Path

def fix_label_files(labels_dir: Path):
    """Fix label files to separate progress comments from YOLO annotations"""
    for label_file in labels_dir.glob("*.txt"):
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            progress_line = None
            bbox_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("# progress:"):
                    progress_line = line
                elif line and not line.startswith("#"):
                    # Validate YOLO format: class_id x_center y_center width height
                    parts = line.split()
                    if len(parts) == 5:
                        try:
                            # Ensure all parts can be converted to float
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            
                            # Validate ranges
                            if (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                                0 <= width <= 1 and 0 <= height <= 1 and
                                class_id >= 0):
                                bbox_lines.append(line)
                            else:
                                print(f"Invalid bbox in {label_file.name}: {line}")
                        except ValueError:
                            print(f"Invalid format in {label_file.name}: {line}")
                    else:
                        print(f"Wrong number of values in {label_file.name}: {line}")
            
            # Rewrite file
            with open(label_file, 'w') as f:
                if progress_line:
                    f.write(progress_line + '\n')
                for bbox_line in bbox_lines:
                    f.write(bbox_line + '\n')
                    
        except Exception as e:
            print(f"Error processing {label_file}: {e}")

if __name__ == "__main__":
    # Fix validation labels
    val_labels = Path("datasets/val/labels")
    if val_labels.exists():
        print("Fixing validation labels...")
        fix_label_files(val_labels)
    
    # Fix train labels
    train_labels = Path("datasets/train/labels")
    if train_labels.exists():
        print("Fixing train labels...")
        fix_label_files(train_labels)
    
    print("Label fixing complete!")