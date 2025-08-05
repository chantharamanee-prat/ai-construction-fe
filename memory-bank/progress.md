# Progress

## What Works
- `evaluate.py` successfully evaluates:
  - Detection metrics via Ultralytics YOLOv8 `model.val()` using `data.yaml`.
  - Progress regression metrics (MAE, RMSE in [0,1]) using the simplified model trained by `train.py` when weights are available.
- Outputs:
  - `reports/evaluation_metrics.csv` (Split, mAP50-95, mAP50, Precision, Recall, Progress_MAE(0-1), Progress_RMSE(0-1))
  - `reports/figures/*.png` when `--save-figs` is used (up to 5 samples).
- CLI arguments provide flexibility for weights, data paths, device, and split control.

## Recent Changes
- `evaluate.py` refactor implemented:
  - Proper Ultralytics v8 API usage for detection evaluation with fallback metric extraction.
  - Regression model loader mirrors `train.py:create_simple_model`.
  - Robust label parsing for `# progress:` with both percent and fractional formats.
  - Added logging and directory creation for reports.
- Documentation added: `docs/EVALUATION_GUIDE.md`.

## What's Left / Next Steps
- Optional: Add confusion matrix and PR/ROC curves exports and include in `reports/figures`.
- Optional: Save per-class AP to CSV/JSON for deeper analysis.
- Optional: Add regression scatter plot (GT vs Pred) and error histograms.
- Optional: Config-driven defaults (pull from `configs/training.yaml` and `configs/dataset.yaml`) to minimize CLI args.
- Optional: Add unit tests for label parsing and regression evaluation paths.

## Known Issues
- If `models/construction_progress.pt` is missing or incompatible, progress metrics are skipped (warning logged).
- `data.yaml` must correctly define the `val`/`test` split used; otherwise detection metrics default to zeros with an error log.
- Progress errors are normalized; convert to percentage by multiplying by 100 for presentation.

## Current Status
- Evaluation pipeline is functional and documented. Ready for PoC evaluation runs on `val` or `test` splits.
