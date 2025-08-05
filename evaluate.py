import argparse
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from custom_dataset import ConstructionProgressDataset
from ultralytics import YOLO


def _setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def _read_progress_from_label(label_path: Path) -> Optional[float]:
    """Read ground-truth progress from a YOLO label file.

    Accepts lines like:
    # progress: 10%
    or
    # progress: 0.1
    Returns value in [0,1] if found, otherwise None.
    """
    if not label_path.exists():
        return None
    try:
        with open(label_path, "r") as f:
            for raw in f:
                line = raw.strip()
                if line.startswith("# progress:"):
                    try:
                        val = line.split(":")[1].strip()
                        if val.endswith("%"):
                            return float(val[:-1]) / 100.0
                        return float(val)
                    except Exception:
                        return None
    except Exception:
        return None
    return None


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _default_transforms(imgsz: int = 640):
    return transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Resize((imgsz, imgsz), antialias=True),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def _load_progress_model(weights_path: Path, device: torch.device) -> Optional[torch.nn.Module]:
    """Load the simplified regression model trained in train.py if available."""
    if not weights_path.exists():
        logging.warning(f"Progress regression weights not found at {weights_path}")
        return None

    # Mirror the architecture from train.py:create_simple_model
    model = torch.nn.Sequential(
        torch.nn.Conv2d(3, 32, 3, padding=1),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(2),
        torch.nn.Conv2d(32, 64, 3, padding=1),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(2),
        torch.nn.Conv2d(64, 128, 3, padding=1),
        torch.nn.ReLU(),
        torch.nn.AdaptiveAvgPool2d(1),
        torch.nn.Flatten(),
        torch.nn.Linear(128, 64),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.2),
        torch.nn.Linear(64, 1),
        torch.nn.Sigmoid(),
    )
    try:
        state = torch.load(weights_path, map_location=device)
        model.load_state_dict(state, strict=True)
        model.to(device)
        model.eval()
        logging.info(f"Loaded progress regression model from {weights_path}")
        return model
    except Exception as e:
        logging.error(f"Failed to load progress regression weights: {e}")
        return None


def _predict_progress(progress_model: torch.nn.Module, image_path: Path, device: torch.device, imgsz: int) -> Optional[float]:
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        logging.warning(f"Failed to open image {image_path}: {e}")
        return None
    tfm = _default_transforms(imgsz)
    with torch.no_grad():
        x = tfm(img).unsqueeze(0).to(device)
        y = progress_model(x).squeeze().item()
    # y is in [0,1]
    return float(y)


def evaluate_model() -> None:
    """Evaluate trained model on validation and test sets.

    - Runs YOLOv8 validation using data.yaml to get standard detection metrics.
    - Optionally evaluates progress regression MAE/RMSE if regression weights exist.
    - Saves visual predictions and a CSV summary to reports/.
    """
    _setup_logging()

    parser = argparse.ArgumentParser(description="Evaluate trained model.")
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="YOLO weights path for detection eval")
    parser.add_argument("--data", type=str, default="data.yaml", help="Path to data.yaml")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=8, help="Batch size for YOLO val")
    parser.add_argument("--device", type=str, default=None, help="CUDA device id like 0 or 'cpu'")
    parser.add_argument("--split", type=str, default="val", choices=["val", "test"], help="Dataset split for progress eval")
    parser.add_argument("--progress-weights", type=str, default="models/construction_progress.pt", help="Progress regression weights saved by train.py")
    parser.add_argument("--save-dir", type=str, default="reports", help="Base directory for reports")
    parser.add_argument("--save-figs", action="store_true", help="Save sample visualizations")
    args = parser.parse_args()

    reports_dir = Path(args.save_dir)
    fig_dir = reports_dir / "figures"
    _ensure_dir(reports_dir)
    _ensure_dir(fig_dir)

    # 1) Detection evaluation via Ultralytics YOLO .val
    # Ultralytics >=8 API: model.val(data=..., imgsz=..., batch=..., device=..., split=...)
    # split: val/test (requires both in data.yaml if used)
    logging.info("Running YOLO detection validation...")
    yolo_model = YOLO(args.weights)
    try:
        # Only run val on the requested split; Ultralytics uses 'val' by default, for 'test' we pass split='test'
        det_results = yolo_model.val(
            data=args.data,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            split=args.split,
            save_json=False,
            verbose=False,
        )
        # det_results.metrics contains ap_class_indexed and map50_95 per docs
        # metrics box:
        mp = getattr(det_results, "box", None)
        # Fallback to overall metrics if structure differs
        if mp is not None:
            det_map50_95 = float(getattr(mp, "map", 0.0))
            det_map50 = float(getattr(mp, "map50", 0.0))
            det_precision = float(getattr(mp, "mp", 0.0))
            det_recall = float(getattr(mp, "mr", 0.0))
        else:
            # Older/newer API fallback
            det_map50_95 = float(getattr(det_results, "map50_95", 0.0))
            det_map50 = float(getattr(det_results, "map50", 0.0))
            det_precision = float(getattr(det_results, "precision", 0.0))
            det_recall = float(getattr(det_results, "recall", 0.0))
        logging.info(f"Detection metrics - mAP50-95: {det_map50_95:.4f}, mAP50: {det_map50:.4f}, P: {det_precision:.4f}, R: {det_recall:.4f}")
    except Exception as e:
        logging.error(f"YOLO detection evaluation failed: {e}")
        det_map50_95 = det_map50 = det_precision = det_recall = 0.0

    # 2) Progress regression evaluation using the simplified model trained in train.py
    # Evaluate over datasets/{split}/images + labels reading "# progress:" line
    progress_mae = progress_rmse = None
    device = torch.device(f"cuda:{args.device}" if (args.device and args.device != "cpu" and torch.cuda.is_available()) else "cpu")
    progress_model = _load_progress_model(Path(args.progress_weights), device)
    if progress_model is not None:
        split_images = Path("datasets") / args.split / "images"
        split_labels = Path("datasets") / args.split / "labels"
        if split_images.exists() and split_labels.exists():
            errors: List[float] = []
            saved = 0
            for img_path in sorted(split_images.glob("*.*")):
                if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                gt = _read_progress_from_label(split_labels / f"{img_path.stem}.txt")
                pred = _predict_progress(progress_model, img_path, device, args.imgsz)
                if gt is None or pred is None:
                    continue
                err = abs(pred - gt)
                errors.append(err)
                if args.save_figs and saved < 5:
                    # produce a simple image with title
                    try:
                        im = Image.open(img_path).convert("RGB")
                        plt.figure(figsize=(6, 4))
                        plt.imshow(im)
                        plt.axis("off")
                        plt.title(f"GT: {gt*100:.1f}% | Pred: {pred*100:.1f}%")
                        plt.tight_layout()
                        plt.savefig(fig_dir / f"{args.split}_{img_path.stem}.png", dpi=150)
                        plt.close()
                        saved += 1
                    except Exception:
                        pass
            if errors:
                errors = np.array(errors, dtype=np.float32)
                progress_mae = float(np.mean(errors))
                progress_rmse = float(np.sqrt(np.mean(errors ** 2)))
                logging.info(f"Progress metrics - MAE: {progress_mae:.4f} (0-1), RMSE: {progress_rmse:.4f} (0-1)")
            else:
                logging.warning("No progress samples found to evaluate.")
        else:
            logging.warning(f"Split folders not found for progress eval: {split_images}, {split_labels}")
    else:
        logging.warning("Skipping progress evaluation (no regression weights).")

    # 3) Write metrics to CSV
    csv_path = reports_dir / "evaluation_metrics.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Split", "mAP50-95", "mAP50", "Precision", "Recall", "Progress_MAE(0-1)", "Progress_RMSE(0-1)"])
        # We log detection metrics for the chosen split to align with progress split
        writer.writerow(
            [
                args.split,
                f"{det_map50_95:.6f}",
                f"{det_map50:.6f}",
                f"{det_precision:.6f}",
                f"{det_recall:.6f}",
                f"{progress_mae:.6f}" if progress_mae is not None else "",
                f"{progress_rmse:.6f}" if progress_rmse is not None else "",
            ]
        )

    logging.info(f"Saved evaluation metrics to {csv_path}")


if __name__ == "__main__":
    evaluate_model()
