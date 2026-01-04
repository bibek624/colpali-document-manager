"""
Configuration file for the Document Manager application
"""

import os

# Qdrant Configuration
QDRANT_URL = "http://localhost:6333"
QDRANT_API_KEY = None  # Set this if your Qdrant instance requires authentication

# File Storage Configuration
# Base directory where PDFs and images are stored
BASE_STORAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "Documents"
)
BASE_STORAGE_PATH = "./Documents"
IMAGES_BASE_PATH = "./Images"

# Ensure directories exist
os.makedirs(BASE_STORAGE_PATH, exist_ok=True)
os.makedirs(IMAGES_BASE_PATH, exist_ok=True)

# ColPali Model Configuration
COLPALI_MODEL_NAME = "vidore/colqwen2.5-v0.2"
VECTOR_SIZE = 128  # For ColQwen2.5

# Processing Configuration
DEFAULT_BATCH_SIZE = 4
DEFAULT_CONVERT_BATCH_SIZE = 10

# UI Configuration
APP_TITLE = "📚 Document Manager"
APP_ICON = "📚"
