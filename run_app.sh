#!/bin/bash

echo "========================================"
echo "  Document Manager - Streamlit App"
echo "========================================"
echo ""

# Check if Qdrant is accessible
echo "Checking Qdrant connection..."
if ! curl -s http://localhost:6333 > /dev/null 2>&1; then
    echo ""
    echo "WARNING: Cannot connect to Qdrant at http://localhost:6333"
    echo "Please ensure Qdrant is running before using the app."
    echo ""
    echo "To start Qdrant with Docker:"
    echo "  docker run -p 6333:6333 qdrant/qdrant"
    echo ""
    read -p "Press Enter to continue..."
fi

echo ""
echo "Starting Document Manager..."
echo ""

# Navigate to the script directory
cd "$(dirname "$0")"

# Run Streamlit
streamlit run app.py





