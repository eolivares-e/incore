#!/bin/bash

echo "Running backend tests..."
cd backend
uv pip install -e ".[dev]"
pytest tests/ -v
