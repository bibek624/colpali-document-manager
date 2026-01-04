# 🚀 Quick Start Guide

## Step 1: Start Qdrant Server

Open a terminal and run:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Or if you have Qdrant installed locally, start it according to your installation method.

Verify it's running by visiting: http://localhost:6333/dashboard

## Step 2: Install Dependencies

Navigate to the document_manager folder and install requirements:

```bash
cd document_manager
pip install -r requirements.txt
```

**Important**: Also install poppler for PDF processing:
- **Windows**: Download from https://github.com/oschwartz10612/poppler-windows/releases/ and add to PATH
- **macOS**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

## Step 3: Run the Application

### Option A: Using the startup script (Windows)
```bash
run_app.bat
```

### Option B: Using the startup script (Mac/Linux)
```bash
chmod +x run_app.sh
./run_app.sh
```

### Option C: Manual start
```bash
streamlit run app.py
```

## Step 4: Access the Web App

Open your browser and go to: **http://localhost:8501**

## Step 5: Get Started

1. **Create a Collection**
   - Click "📁 Collections" in the sidebar
   - Enter a collection name (e.g., "research_papers")
   - Click "Create Collection"

2. **Upload a Document**
   - Click "📤 Upload Document" in the sidebar
   - Select your collection
   - Upload a PDF file
   - Click "🚀 Process and Index Document"
   - Wait for processing to complete

3. **Manage Your Documents**
   - Click "🗑️ Manage Documents" in the sidebar
   - Select a collection
   - View, search, and delete documents

## Troubleshooting

### "Cannot connect to Qdrant"
- Ensure Qdrant is running: `docker ps` should show qdrant container
- Check if port 6333 is accessible: `curl http://localhost:6333`

### "Module not found" errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- The app automatically adds parent directory to Python path

### "PDF conversion failed"
- Install poppler-utils (see Step 2)
- Verify installation: `pdftoppm -h` (should show help text)

### GPU/Memory issues
- Reduce batch sizes in the upload options
- Default batch size: 4 (embedding), 10 (conversion)
- Lower values use less memory but take longer

## Configuration

Edit `config.py` to customize:
- Qdrant URL (if not using default localhost:6333)
- Storage paths for PDFs and images
- Model settings and batch sizes

## Tips

- Use descriptive collection names for better organization
- Lower batch sizes if you have limited GPU memory
- The app shows real-time progress during document processing
- All images are automatically saved and can be previewed
- Deleting a document removes both vectors and images

## Need Help?

Check the full README.md for detailed documentation and troubleshooting.





