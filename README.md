# Document Manager Application

A beautiful Streamlit-based web application for managing Qdrant vector stores and documents using ColPali for document processing.

## Features

- 🗄️ **Collection Management**: Create, view, and delete Qdrant collections
- 📤 **Document Upload**: Upload PDF documents for processing and indexing
- 🔍 **Vector Search**: Efficient document retrieval using ColPali embeddings
- 🗑️ **Document Management**: View and delete indexed documents
- 📊 **Dashboard**: Overview statistics and quick actions
- 🎨 **Beautiful UI**: Modern, clean interface with gradient designs

## Prerequisites

- Python 3.8+
- Qdrant running locally at `http://localhost:6333`
- CUDA-capable GPU (recommended for faster processing)

## Installation

1. Install required dependencies:

```bash
pip install streamlit qdrant-client colpali-engine torch pdf2image PyPDF2 Pillow python-dotenv
```

2. For `pdf2image`, you also need to install poppler:
   - **Windows**: Download from https://github.com/oschwartz10612/poppler-windows/releases/
   - **macOS**: `brew install poppler`
   - **Linux**: `sudo apt-get install poppler-utils`

## Running the Application

1. Ensure Qdrant is running locally:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. Navigate to the document_manager directory:

```bash
cd document_manager
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

4. Open your browser and go to `http://localhost:8501`

## Usage

### 1. Create a Collection
- Navigate to the **Collections** page
- Enter a unique collection name
- Set the vector size (default: 128 for ColQwen2.5)
- Click "Create Collection"

### 2. Upload Documents
- Go to the **Upload Document** page
- Select a collection from the dropdown
- Upload a PDF file
- Adjust batch sizes if needed
- Click "Process and Index Document"

### 3. Manage Documents
- Visit the **Manage Documents** page
- Select a collection
- View, search, and delete documents
- Preview document images

## Configuration

Edit `config.py` to customize:

- `QDRANT_URL`: Qdrant server URL (default: http://localhost:6333)
- `BASE_STORAGE_PATH`: Where PDFs are stored
- `IMAGES_BASE_PATH`: Where extracted images are saved
- `COLPALI_MODEL_NAME`: ColPali model to use
- `VECTOR_SIZE`: Vector dimension for embeddings

## Directory Structure

```
document_manager/
├── app.py                  # Main Streamlit application
├── config.py              # Configuration settings
├── qdrant_manager.py      # Qdrant operations module
├── pages/
│   ├── __init__.py
│   ├── home_page.py       # Dashboard page
│   ├── collections_page.py # Collection management
│   ├── upload_page.py     # Document upload
│   └── manage_page.py     # Document management
└── README.md
```

## Notes

- The application uses ColQwen2.5 for document embeddings
- Multivector configuration is used for optimal ColPali performance
- Images are automatically saved when documents are processed
- All document deletions also remove associated images
- The app maintains unique document IDs to prevent conflicts

## Troubleshooting

**Connection Error**: Ensure Qdrant is running at the configured URL

**GPU Memory Issues**: Reduce batch sizes in processing options

**PDF Conversion Fails**: Verify poppler is installed correctly

**Import Errors**: Ensure all parent modules are in the Python path





