#!/bin/bash

export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

export YOLO_VERBOSE=False
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1

gunicorn api:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 1 \
    --bind 0.0.0.0:8000 \
    --chdir server \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload
