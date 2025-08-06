# System Patterns

## System architecture
Monolithic

## Key technical decisions
- Using YOLOv8 for object detection
- Python-based implementation
- Ultralytics framework
- Extended YOLOv8 model with regression head for construction progress prediction
- Custom dataset loader for multi-task learning (detection + progress regression)
- Custom training loop integrating detection and regression losses
- Separate but coordinated evaluation paths: Ultralytics detection validation + simplified regression evaluation

## Design patterns and best practices
### API Design
- RESTful API design with FastAPI
- Separation of concerns:
  - Routes handle HTTP layer
  - Handlers manage business logic
  - Models define data schemas
- Error handling:
  - HTTPException for client errors
  - 500 for server errors with details
- Filesystem operations use pathlib for cross-platform compatibility

### Configuration Management
- External YAML files for annotation, dataset splitting, and training parameters
- Error handling with logging for robust operation and debugging
- Logging standards set to DEBUG/INFO level for detailed traceability
- Use of pathlib for path management to improve cross-platform compatibility
- Modular code organization separating annotation, data processing, training, and evaluation
- Adoption of type hints and docstrings for improved code readability and maintainability
- CLI-driven scripts for reproducibility (train and evaluate support arguments)

## Critical implementation paths
1. Data preprocessing pipeline
2. Model training configuration
3. Inference API
4. Evaluation pipeline
   - Detection metrics via `ultralytics.YOLO(...).val(data, split, imgsz, batch, device)`
   - Progress regression metrics using the simplified model architecture (mirrors `train.py:create_simple_model`)
   - Label parsing for `# progress:` line (supports `%` and fraction formats)
   - Metrics aggregation to `reports/evaluation_metrics.csv` and optional figures in `reports/figures`

## Evaluation Pipeline Details (Current)
- Detection:
  - Inputs: `--weights` (e.g., `yolov8n.pt`), `--data`, `--split` (`val`/`test`), `--imgsz`, `--batch`, `--device`
  - Metrics extraction compatible with Ultralytics 8.3.174 (`box.map`, `box.map50`, `box.mp`, `box.mr`) with safe fallbacks
- Progress Regression:
  - Inputs: `--progress-weights` (`models/construction_progress.pt`)
  - Reads GT progress from YOLO label comment line: `# progress: 10%` or `# progress: 0.1`
  - Evaluates MAE and RMSE in [0,1]

## Artifacts
- `reports/evaluation_metrics.csv`
  - Columns: Split, mAP50-95, mAP50, Precision, Recall, Progress_MAE(0-1), Progress_RMSE(0-1)
- `reports/figures/*.png` (optional with `--save-figs`)

## Future Extensions
- Add confusion matrix and PR/ROC curve exports from Ultralytics validation
- Per-class AP breakdown exported to CSV/JSON
- Regression scatter plots (GT vs Pred) and error histograms
- Config-driven defaults sourced from `configs/training.yaml`/`configs/dataset.yaml`
- Unit tests for label parsing and evaluation routines
