#!/bin/bash
# Setup script for Vernacular Medical Parser

echo "Setting up Vernacular Medical Parser..."

# Create directories
mkdir -p data/prescriptions/{raw,clean,annotations}
mkdir -p data/lab_reports/raw
mkdir -p data/drug_list
mkdir -p data/interactions
mkdir -p data/vault
mkdir -p models/ocr
mkdir -p models/embeddings

# Install Tesseract (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "Installing Tesseract OCR..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr
    sudo apt-get install -y tesseract-ocr-hin tesseract-ocr-tel tesseract-ocr-tam
fi

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Download language models
echo "Downloading language models..."
python -c "
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
print('Downloading translation models...')
tokenizer = AutoTokenizer.from_pretrained('ai4bharat/indictrans2-en-indic-1B', trust_remote_code=True)
"

# Initialize database
echo "Initializing database..."
python -c "from database.db_init import init_database; init_database()"

echo "Setup complete!"
echo "Please configure your API keys in .env file"