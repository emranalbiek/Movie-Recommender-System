#!/bin/bash

echo "=========================================="
echo "Movie Recommender System - Setup"
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv recommender-system

# Activate virtual environment
echo "Activating virtual environment..."
source recommender-system/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p artifacts
mkdir -p data

# Save the artifacts for runing the application
echo "Saving artifacts..."
python3 main.py

echo "=========================================="
echo "Setup completed successfully!"
echo "Run './run.sh' to start the application"
echo "=========================================="
