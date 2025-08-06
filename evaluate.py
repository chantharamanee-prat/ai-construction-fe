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
import yaml

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


def _load_yaml_config(path: str) -> dict:
    """Safely load a YAML config file, returning an empty dict if not found or invalid."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def evaluate_model() -> None:
    """Evaluate trained model on validation and test sets.

    - Runs YOLOv8 validation using data.yaml to get standard detection metrics.
    - Optionally evaluates progress regression MAE/RMSE if regression weights exist.
    - Saves visual predictions and a CSV summary to reports/.
    """
    _setup_logging()

    # Load config defaults
    training_cfg = _load_yaml_config("configs/training.yaml")
    dataset_cfg = _load_yaml_config("configs/dataset.yaml")

    # Map config values to CLI defaults
    cli_defaults = {
        "weights": "models/yolov8n.pt",  # No direct config, keep as fallback
        "data": training_cfg.get("data", "data.yaml"),
        "imgsz": training_cfg.get("imgsz", 640),
        "batch": training_cfg.get("batch", 8),
        "device": str(training_cfg.get("device")) if "device" in training_cfg else None,
        "split": "val",
        "progress_weights": training_cfg.get("save_path", "models/construction_progress.pt"),
        "save_dir": "reports",
    }

    parser = argparse.ArgumentParser(description="Evaluate trained model. Defaults are loaded from configs/training.yaml if available.")
    parser.add_argument("--weights", type=str, default=cli_defaults["weights"], help="YOLO weights path for detection eval (default: from config or 'yolov8n.pt')")
    parser.add_argument("--data", type=str, default=cli_defaults["data"], help="Path to data.yaml (default: from config or 'data.yaml')")
    parser.add_argument("--imgsz", type=int, default=cli_defaults["imgsz"], help="Image size (default: from config or 640)")
    parser.add_argument("--batch", type=int, default=cli_defaults["batch"], help="Batch size for YOLO val (default: from config or 8)")
    parser.add_argument("--device", type=str, default=cli_defaults["device"], help="CUDA device id like 0 or 'cpu' (default: from config or None)")
    parser.add_argument("--split", type=str, default=cli_defaults["split"], choices=["val", "test"], help="Dataset split for progress eval (default: 'val')")
    parser.add_argument("--progress-weights", type=str, default=cli_defaults["progress_weights"], help="Progress regression weights saved by train.py (default: from config or 'models/construction_progress.pt')")
    parser.add_argument("--save-dir", type=str, default=cli_defaults["save_dir"], help="Base directory for reports (default: 'reports')")
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


import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve, auc

def _plot_confusion_matrix(y_true, y_pred, classes, save_path: Path) -> None:
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def _plot_pr_roc_curves(y_true, y_scores, save_dir: Path) -> None:
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(recall, precision, color="b", lw=2)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")

    plt.subplot(1, 2, 2)
    plt.plot(fpr, tpr, color="r", lw=2, label=f"AUC = {roc_auc:.2f}")
    plt.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(save_dir / "pr_roc_curves.png")
    plt.close()

def evaluate_model() -> None:
    """Evaluate trained model on validation and test sets.

    - Runs YOLOv8 validation using data.yaml to get standard detection metrics.
    - Optionally evaluates progress regression MAE/RMSE if regression weights exist.
    - Saves visual predictions and a CSV summary to reports/.
    """
    _setup_logging()

    # Load config defaults
    training_cfg = _load_yaml_config("configs/training.yaml")
    dataset_cfg = _load_yaml_config("configs/dataset.yaml")

    # Map config values to CLI defaults
    cli_defaults = {
        "weights": "yolov8n.pt",  # No direct config, keep as fallback
        "data": training_cfg.get("data", "data.yaml"),
        "imgsz": training_cfg.get("imgsz", 640),
        "batch": training_cfg.get("batch", 8),
        "device": str(training_cfg.get("device")) if "device" in training_cfg else None,
        "split": "val",
        "progress_weights": training_cfg.get("save_path", "models/construction_progress.pt"),
        "save_dir": "reports",
    }

    parser = argparse.ArgumentParser(description="Evaluate trained model. Defaults are loaded from configs/training.yaml if available.")
    parser.add_argument("--weights", type=str, default=cli_defaults["weights"], help="YOLO weights path for detection eval (default: from config or 'yolov8n.pt')")
    parser.add_argument("--data", type=str, default=cli_defaults["data"], help="Path to data.yaml (default: from config or 'data.yaml')")
    parser.add_argument("--imgsz", type=int, default=cli_defaults["imgsz"], help="Image size (default: from config or 640)")
    parser.add_argument("--batch", type=int, default=cli_defaults["batch"], help="Batch size for YOLO val (default: from config or 8)")
    parser.add_argument("--device", type=str, default=cli_defaults["device"], help="CUDA device id like 0 or 'cpu' (default: from config or None)")
    parser.add_argument("--split", type=str, default=cli_defaults["split"], choices=["val", "test"], help="Dataset split for progress eval (default: 'val')")
    parser.add_argument("--progress-weights", type=str, default=cli_defaults["progress_weights"], help="Progress regression weights saved by train.py (default: from config or 'models/construction_progress.pt')")
    parser.add_argument("--save-dir", type=str, default=cli_defaults["save_dir"], help="Base directory for reports (default: 'reports')")
    parser.add_argument("--save-figs", action="store_true", help="Save sample visualizations")
    parser.add_argument("--save-curves", action="store_true", help="Save confusion matrix and PR/ROC curves")
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

        # Save confusion matrix and PR/ROC curves if requested
        if args.save_curves:
            # Prepare data for confusion matrix and curves
            # Extract true labels and predicted scores for binary classification per class
            # For simplicity, use det_results.ap_class_indexed and det_results.box.confidence or similar
            # This is a placeholder: actual extraction depends on det_results structure
            # Here we simulate binary labels and scores for the first class as example
            classes = det_results.names if hasattr(det_results, "names") else [str(i) for i in range(len(det_results.ap_class_indexed))]
            # For confusion matrix, we need y_true and y_pred arrays
            # For PR/ROC curves, we need y_true and y_scores arrays
            # Since det_results does not expose these directly, this is a limitation
            # We will skip actual plotting here unless we can access raw predictions and labels
            logging.warning("Confusion matrix and PR/ROC curve plotting requires raw prediction and label data, which is not available in det_results. Skipping.")
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
            gt_values: List[float] = []
            pred_values: List[float] = []
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
                gt_values.append(gt)
                pred_values.append(pred)
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

                # Save regression scatter plot and error histogram if requested
                if args.save_figs:
                    try:
                        plt.figure(figsize=(6, 6))
                        plt.scatter(gt_values, pred_values, alpha=0.6)
                        plt.plot([0, 1], [0, 1], "r--")
                        plt.xlabel("Ground Truth Progress")
                        plt.ylabel("Predicted Progress")
                        plt.title("Regression Scatter Plot (GT vs Pred)")
                        plt.tight_layout()
                        plt.savefig(fig_dir / f"{args.split}_regression_scatter.png", dpi=150)
                        plt.close()

                        plt.figure(figsize=(6, 4))
                        plt.hist(errors, bins=20, alpha=0.7)
                        plt.xlabel("Absolute Error")
                        plt.ylabel("Frequency")
                        plt.title("Regression Error Histogram")
                        plt.tight_layout()
                        plt.savefig(fig_dir / f"{args.split}_regression_error_hist.png", dpi=150)
                        plt.close()
                    except Exception as e:
                        logging.warning(f"Failed to save regression plots: {e}")
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
