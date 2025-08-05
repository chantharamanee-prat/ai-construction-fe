# Active Context

## Current Focus
- Implemented robust evaluation pipeline for detection (YOLOv8) and progress regression (custom simplified model) in `evaluate.py`.
- Standardized outputs: CSV summary and optional figures for qualitative inspection.

## Recent Changes
- Refactored `evaluate.py` to:
  - Use Ultralytics YOLOv8 `model.val()` for detection metrics against `data.yaml`.
  - Load and evaluate the simplified regression model trained in `train.py` (architecture mirrored) from `models/construction_progress.pt`.
  - Read ground-truth progress from YOLO label files using comment line format: `# progress: 10%` or `# progress: 0.1` (normalized to [0,1]).
  - CLI args for flexibility: `--weights`, `--data`, `--imgsz`, `--batch`, `--device`, `--split`, `--progress-weights`, `--save-dir`, `--save-figs`.
  - Save metrics to `reports/evaluation_metrics.csv`; optional visualizations to `reports/figures`.

## How Evaluation Works Now
- Detection:
  - Command: `python evaluate.py --weights yolov8n.pt --data data.yaml --split val`
  - Metrics extracted from `YOLO(...).val(...)` compatible with Ultralytics 8.3.174:
    - mAP50-95 (`box.map`), mAP50 (`box.map50`), Precision (`box.mp`), Recall (`box.mr`) with fallbacks if structure changes.
- Progress Regression:
  - Loads `models/construction_progress.pt` if present.
  - Evaluates MAE and RMSE in [0,1] range over `datasets/{split}/images` + corresponding labels in `datasets/{split}/labels`.
  - Optional figures (first 5) saved if `--save-figs` is passed.

## Outputs
- `reports/evaluation_metrics.csv`
  - Columns: Split, mAP50-95, mAP50, Precision, Recall, Progress_MAE(0-1), Progress_RMSE(0-1)
- `reports/figures/*.png` (if `--save-figs`)

## Next Steps
- Optional: add confusion matrix, PR/ROC curves via Ultralytics settings and export key plots to `reports/figures`.
- Optional: aggregate per-class AP and log to an extended CSV/JSON.
- Optional: add regression scatter plots (GT vs Pred) and error histograms.
- Optional: parameterize the number of saved visualization samples.

## Important Patterns & Preferences
- Use `logging` for progress and errors.
- Use `pathlib.Path`.
- Keep evaluation CLI consistent with training configs (`configs/training.yaml`, `configs/dataset.yaml`).
- Normalize progress in [0,1]; label format must include the `# progress:` comment line.

## Known Issues / Considerations
- If `models/construction_progress.pt` does not exist or incompatible, progress evaluation is skipped with a warning.
- Requires `data.yaml` to define `val` and `test` if those splits are used for detection evaluation.
- Label files must contain a `# progress:` line for samples to count towards progress metrics.
