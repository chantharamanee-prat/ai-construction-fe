# Technical Context

## Technologies used
- Python 3.8+
- Ultralytics (includes: numpy, matplotlib, opencv-python, pillow, pyyaml, requests, scipy, torch, torchvision, tqdm, psutil, py-cpuinfo, pandas, ultralytics-thop)

## Development setup
- Virtual environment configured
- Installation: `pip install -r requirements.txt`

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
