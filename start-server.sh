#!/bin/bash

uvicorn api:app --host 0.0.0.0 --port 8000 --app-dir server --workers 2 --worker-class uvicorn.workers.UvicornWorker