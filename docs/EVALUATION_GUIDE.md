# Evaluation Guide

This guide explains how to evaluate both object detection (YOLOv8) and progress regression (custom simplified model) using `evaluate.py`.

## Overview

The evaluation pipeline performs:
1) Detection metrics via Ultralytics YOLOv8 `model.val()` against the dataset defined in `data.yaml`.
2) Progress regression metrics (MAE, RMSE in [0,1]) using the simplified model trained by `train.py`, if the weights exist.

Outputs:
- CSV summary: `reports/evaluation_metrics.csv`
- Optional qualitative figures: `reports/figures/*.png` (first 5 images per run when `--save-figs` is used)

## Prerequisites

- Python environment set up: `pip install -r requirements.txt` (Ultralytics 8.3.174)
- `data.yaml` with valid paths for `train`, `val`, and optionally `test`
- Dataset folder structure:
  ```
  datasets/
    train/
      images/
      labels/
    val/
      images/
      labels/
    test/
      images/
      labels/
  ```
- Label files use YOLO format with an additional comment line for progress:
  ```
  # progress: 10%
  # or
  # progress: 0.1
  class_id x_center y_center width height
  ...
  ```
  Progress is normalized to [0,1] internally. If not present, that sample is skipped for progress metrics.

- For progress regression:
  - Trained weights saved by `train.py` at `models/construction_progress.pt` (or provide a custom path via `--progress-weights`).

## CLI Usage

Basic detection evaluation (validation split):
```
python evaluate.py --weights yolov8n.pt --data data.yaml --split val
```

Detection on test split + progress regression (if weights exist):
```
python evaluate.py \
  --weights yolov8n.pt \
  --data data.yaml \
  --split test \
  --progress-weights models/construction_progress.pt \
  --save-figs
```

Common arguments:
- `--weights`: YOLO detection weights (default: `yolov8n.pt`)
- `--data`: Path to data.yaml (default: `data.yaml`)
- `--imgsz`: Image size for evaluation (default: 640)
- `--batch`: Batch size for YOLO validation (default: 8)
- `--device`: CUDA device (e.g., `0`) or `cpu` (default: auto)
- `--split`: Which split to evaluate against for both detection and progress (choices: `val`, `test`; default: `val`)
- `--progress-weights`: Path to regression weights (default: `models/construction_progress.pt`)
- `--save-dir`: Base directory for reports (default: `reports`)
- `--save-figs`: If provided, saves up to 5 visualization images

## Outputs and Interpretation

- CSV: `reports/evaluation_metrics.csv`
  - Columns:
    - `Split`: `val` or `test`
    - `mAP50-95`: Mean Average Precision across IoU 0.50 to 0.95 (detection)
    - `mAP50`: mAP at IoU 0.50 (detection)
    - `Precision`, `Recall`: Overall detection precision and recall
    - `Progress_MAE(0-1)`, `Progress_RMSE(0-1)`: Regression errors normalized to [0,1]
- Figures: `reports/figures/*.png` (if `--save-figs`)
  - Simple visuals labeling GT vs predicted progress for up to 5 images

Note: Progress metrics report errors in normalized [0,1] units. To view them as percentages, multiply by 100.

## How It Works Internally

- Detection:
  - Uses `ultralytics.YOLO(args.weights).val(data=args.data, split=args.split, imgsz, batch, device)`
  - Extracts metrics from the returned results object; supports Ultralytics 8.3.174 structure with safe fallbacks
- Progress:
  - Loads the simplified model architecture that matches `train.py:create_simple_model`
  - Loads `--progress-weights` and runs a forward pass on each image in `datasets/{split}/images`
  - Reads GT progress from `datasets/{split}/labels/<name>.txt` via the `# progress:` line
  - Computes MAE and RMSE in [0,1]

## Troubleshooting

- Missing regression weights:
  - Warning is logged and progress metrics are skipped
  - Ensure `models/construction_progress.pt` exists or pass a valid path in `--progress-weights`
- No progress samples found:
  - Ensure label files contain a `# progress:` line (e.g., `# progress: 10%` or `# progress: 0.1`)
- Invalid `data.yaml`:
  - Ensure `val`/`test` keys are present if using those splits
  - Paths under `train`, `val`, `test` should point to directories containing `images` and `labels`
- GPU/CPU device issues:
  - Use `--device cpu` to force CPU
  - Use `--device 0` (or appropriate id) for CUDA if available
- Figures not saved:
  - Only saved when `--save-figs` is specified
  - Limited to first 5 images per run

## Examples

Val split, detection only:
```
python evaluate.py --weights yolov8n.pt --data data.yaml --split val
```

Test split, detection + progress, save figures:
```
python evaluate.py --weights yolov8n.pt --data data.yaml --split test --progress-weights models/construction_progress.pt --save-figs
```

Larger image size, specific GPU:
```
python evaluate.py --weights yolov8n.pt --data data.yaml --imgsz 768 --device 0
```

## Notes and Extensions

- You can extend the script to export confusion matrices and PR curves by enabling Ultralytics save options and copying outputs to `reports/figures`.
- Consider adding a scatter plot of GT vs predicted progress and error histograms for deeper analysis.
