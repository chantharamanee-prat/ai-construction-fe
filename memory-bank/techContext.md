# Technical Context

## Technologies used
- Python 3.8+
- Ultralytics (includes: numpy, matplotlib, opencv-python, pillow, pyyaml, requests, scipy, torch, torchvision, tqdm, psutil, py-cpuinfo, pandas, ultralytics-thop)

## Development setup
- Virtual environment configured
- Installation: `pip install -r requirements.txt`

## Directory Structure
Server-side code is organized under `server/`:
- `api_handlers/`: API business logic handlers
- `configs/`: YAML configuration files
- `datasets/`: Raw and processed datasets
- `dto/`: Data transfer objects
- `docs/`: Documentation
- `models/`: Model weights and definitions
- `reports/`: Evaluation metrics and figures

## Technical constraints
- Dataset limited to 50% completion
- GPU requirements for training

## Coding standards
- Follow PEP8 style guide
- Use type hints for all functions and methods
- Include Google-style docstrings for all modules, classes, and functions
- Use pathlib for file and path operations
- Use logging module for debug and info messages

## Testing
- Use pytest for unit testing

## Dependencies
### requirements.txt
ultralytics==8.3.174
fastapi==0.109.1
uvicorn==0.27.0
python-multipart==0.0.6

## API Implementation
- Framework: FastAPI
- Endpoints:
  - GET /api/images - Lists available images with annotation status and progress
    - Returns: List[ImageDTO] where:
      - path: str (image path)
      - annotated: bool
      - progress: float (0-1.0)
  - GET /api/images/{image_path} - Serves image file
  - POST /api/annotations - Saves/updates annotation data including progress
- Middleware: CORS configured to allow all origins
- Data Flow:
  - API routes delegate to handler modules
  - Uses pathlib for filesystem operations
  - Models define request/response schemas
- New DTOs:
  - ImageDTO: For image listing responses
  - Annotation: Updated with progress field

## Evaluation Implementation (Current)
- Detection evaluation:
  - API: `from ultralytics import YOLO` then `YOLO(weights).val(data=data_yaml, imgsz, batch, device, split)`
  - Metrics extracted with compatibility for Ultralytics 8.3.174 (`results.box.map`, `results.box.map50`, `results.box.mp`, `results.box.mr`), with fallbacks.
- Progress regression evaluation:
  - Simplified CNN architecture mirroring `train.py:create_simple_model` (Conv2d → ReLU → MaxPool x2 → Conv2d → GAP → FC → Sigmoid) producing normalized progress in [0,1].
  - Weights loaded from `models/construction_progress.pt` (configurable via `--progress-weights`).
  - Ground-truth read from YOLO label comment `# progress:` in either percent (e.g., `10%`) or fractional (`0.1`) form.

## Script Interfaces
- `evaluate.py` CLI:
  - `--weights`, `--data`, `--imgsz`, `--batch`, `--device`, `--split {val,test}`, `--progress-weights`, `--save-dir`, `--save-figs`
- Outputs:
  - `reports/evaluation_metrics.csv`
  - `reports/figures/*.png` (optional with `--save-figs`)
- Documentation:
  - `docs/EVALUATION_GUIDE.md` documents usage, requirements, outputs, and troubleshooting.

## Notes
- Progress metrics are reported in [0,1]. Multiply by 100 for percentage interpretation.
- If regression weights are missing or incompatible, progress evaluation is skipped with a warning.
- `data.yaml` must define the requested split (`val` or `test`) for detection evaluation to run normally.
