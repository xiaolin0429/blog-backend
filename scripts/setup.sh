#!/bin/bash

echo "Installing PostgreSQL..."
brew install postgresql@14
brew services start postgresql@14

echo "Installing Redis..."
brew install redis
brew services start redis

echo "Installing Elasticsearch..."
brew install elasticsearch
brew services start elasticsearch

echo "Installing MinIO..."
brew install minio
brew services start minio

echo "Creating PostgreSQL database..."
createdb blog_db

echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
