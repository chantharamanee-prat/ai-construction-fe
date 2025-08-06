# Product Context

## API Role
- Enables annotation workflow between frontend and backend
- Provides endpoints for:
  - Listing available images
  - Serving image files
  - Saving annotations
- Designed to support the construction progress monitoring PoC

## Why this project exists
To assess the feasibility of using YOLO models for construction progress monitoring.

## Problems it solves
- Automated progress tracking for construction projects
- Objective completion percentage estimation

## How it should work
1. Capture site images at regular intervals
2. Process images through YOLO model
3. Generate completion percentage reports

## User experience goals
- Simple image upload interface
- Clear progress visualization
- Exportable reports
