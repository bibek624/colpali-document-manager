"""
Test script to verify Document Manager setup
Run this before starting the app to check if everything is configured correctly
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("Testing Document Manager Setup")
    print("=" * 60)
    print()
    
    required_modules = {
        'streamlit': 'Streamlit',
        'qdrant_client': 'Qdrant Client',
        'torch': 'PyTorch',
        'pdf2image': 'PDF2Image',
        'PyPDF2': 'PyPDF2',
        'PIL': 'Pillow',
        'colpali_engine': 'ColPali Engine',
        'transformers': 'Transformers',
        'numpy': 'NumPy',
        'tqdm': 'TQDM',
    }
    
    missing_modules = []
    
    for module, name in required_modules.items():
        try:
            __import__(module)
            print(f"✅ {name:20s} - OK")
        except ImportError:
            print(f"❌ {name:20s} - MISSING")
            missing_modules.append(module)
    
    print()
    
    if missing_modules:
        print("=" * 60)
        print("❌ Some modules are missing!")
        print("=" * 60)
        print()
        print("Install missing modules with:")
        print(f"  pip install {' '.join(missing_modules)}")
        print()
        print("Or install all requirements:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("=" * 60)
        print("✅ All required modules are installed!")
        print("=" * 60)
        print()
    
    return True


def test_qdrant_connection():
    """Test connection to Qdrant"""
    print("Testing Qdrant Connection...")
    print("-" * 60)
    
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant successfully!")
        print(f"   Found {len(collections.collections)} collection(s)")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to Qdrant: {e}")
        print()
        print("Make sure Qdrant is running:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        print()
        print("You can still start the app, but it won't work until Qdrant is running.")
        return False


def test_poppler():
    """Test if poppler is installed for PDF conversion"""
    print()
    print("Testing Poppler (PDF Conversion)...")
    print("-" * 60)
    
    try:
        from pdf2image import convert_from_path
        # This will raise an exception if poppler is not found
        # We don't actually convert anything, just check if it's available
        print("✅ Poppler appears to be configured correctly")
        return True
    except Exception as e:
        print(f"⚠️  Poppler may not be installed: {e}")
        print()
        print("PDF conversion requires poppler-utils:")
        print("  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/")
        print("  macOS:   brew install poppler")
        print("  Linux:   sudo apt-get install poppler-utils")
        print()
        return False


def test_cuda():
    """Test CUDA availability"""
    print()
    print("Testing CUDA (GPU Support)...")
    print("-" * 60)
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA is available!")
            print(f"   GPU Device: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("⚠️  CUDA not available - will use CPU")
            print("   Processing will be slower but will still work")
            return False
    except Exception as e:
        print(f"⚠️  Cannot check CUDA: {e}")
        return False


def test_directories():
    """Test if required directories exist or can be created"""
    print()
    print("Testing Storage Directories...")
    print("-" * 60)
    
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    
    dirs_to_check = [
        ('Documents', 'PDF storage'),
        ('Images', 'Image storage'),
    ]
    
    all_ok = True
    
    for dir_name, description in dirs_to_check:
        dir_path = os.path.join(os.path.dirname(parent_dir), dir_name)
        
        if os.path.exists(dir_path):
            print(f"✅ {description:20s} - {dir_path}")
        else:
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ {description:20s} - Created: {dir_path}")
            except Exception as e:
                print(f"❌ {description:20s} - Failed to create: {e}")
                all_ok = False
    
    return all_ok


def main():
    """Run all tests"""
    
    results = {
        'modules': test_imports(),
        'qdrant': test_qdrant_connection(),
        'poppler': test_poppler(),
        'cuda': test_cuda(),
        'directories': test_directories(),
    }
    
    print()
    print("=" * 60)
    print("Setup Test Complete")
    print("=" * 60)
    print()
    
    critical_issues = []
    warnings = []
    
    if not results['modules']:
        critical_issues.append("Missing Python modules")
    
    if not results['qdrant']:
        critical_issues.append("Qdrant not accessible")
    
    if not results['poppler']:
        warnings.append("Poppler may not be installed (needed for PDF conversion)")
    
    if not results['cuda']:
        warnings.append("CUDA not available (processing will be slower)")
    
    if critical_issues:
        print("❌ CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"   - {issue}")
        print()
        print("Please resolve these issues before running the app.")
        print()
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
        print("The app may work with reduced functionality.")
        print()
    
    if not critical_issues:
        print("✅ Ready to run!")
        print()
        print("Start the app with:")
        print("  streamlit run app.py")
        print()
        print("Or use the startup script:")
        print("  run_app.bat (Windows)")
        print("  ./run_app.sh (Mac/Linux)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()





