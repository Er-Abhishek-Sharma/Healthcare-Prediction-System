#!/usr/bin/env bash
set -o errexit   # exit on any error

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Seed the database with diseases and symptoms
python manage.py seed_data

# Train the ML models (uses synthetic data if no dataset provided)
python manage.py train_models