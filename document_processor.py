import os
import shutil
from datetime import datetime
import torch
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from tqdm import tqdm
import gc
import config
from metadata_store import MetadataStore

# Initialize MetadataStore
metadata_store = MetadataStore()

class DocumentProcessor:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
        
        # Initialize ColPali model
        # Note: Importing here to avoid heavy load if not processing
        from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
        
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.colpali_model = ColQwen2_5.from_pretrained(
            config.COLPALI_MODEL_NAME,
            torch_dtype=torch.bfloat16,
            device_map=self.device,
        )
        self.colpali_processor = ColQwen2_5_Processor.from_pretrained(
            config.COLPALI_MODEL_NAME, use_fast=True
        )

    def process_document(
        self,
        temp_file_path: str,
        original_filename: str,
        batch_size: int = 4,
        convert_batch_size: int = 10,
        progress_callback = None
    ):
        """
        Process document: Save PDF, Index to Qdrant, Save Images, Update Metadata
        
        Args:
            temp_file_path: Path to temporary PDF file
            original_filename: Original name of the uploaded file
            batch_size: Batch size for embedding generation
            convert_batch_size: Batch size for PDF conversion
            progress_callback: Optional callback function(current_page, total_pages) for progress updates
        """
        # 1. Generate Unique ID and Paths
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = os.path.splitext(original_filename)[0]
        unique_id = f"{base_name}_{timestamp}"
        
        # Create Documents directory if not exists
        documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Documents")
        os.makedirs(documents_dir, exist_ok=True)
        
        # Save PDF with unique name
        saved_pdf_path = os.path.join(documents_dir, f"{unique_id}.pdf")
        shutil.copy2(temp_file_path, saved_pdf_path)
        
        print(f"🔄 Processing: {original_filename}")
        print(f"🆔 Unique ID: {unique_id}")
        
        # 2. Get PDF Info
        try:
            with open(saved_pdf_path, "rb") as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
            
        # 3. Store Metadata
        metadata_store.add_document(unique_id, {
            "unique_id": unique_id,
            "original_name": original_filename,
            "total_pages": total_pages,
            "upload_date": timestamp,
            "collection": self.collection_name,
            "pdf_path": saved_pdf_path
        })

        # 4. Process Pages
        global_page_idx = 0 # Need a strategy for global ID if we want to avoid collisions across documents?
        # Ideally, Qdrant Point IDs should be unique. Using UUIDs or a hash is safer than global_page_idx starting at 0 for each doc.
        # But if the user's previous code used global_page_idx starting at 0, it might overwrite? 
        # The previous code used global_page_idx = 0 inside the loop. 
        # Wait, the previous code in `rag_pipeline.py`:
        # `global_page_idx = 0` inside `_process_document_in_batches`
        # `points.append(qdrant_models.PointStruct(id=global_page_idx...))`
        # This implies it OVERWRITES points 0, 1, 2... for EVERY document if they share the same collection!
        # This is a BUG in the original pipeline if multiple documents are in the same collection.
        # FIX: Use UUIDs for points.
        
        import uuid

        for start_page in range(0, total_pages + 1, batch_size): # Logic from rag_pipeline seems to be chunking by batch_size for processing?
            # Wait, the loop in rag_pipeline is `for start_page in range(0, total_pages + 1, batch_size):`
            # But converting is done in `convert_batch_size`?
            # Actually rag_pipeline iterates `batch_size` at a time.
            
            # Let's clean up the loop logic to be robust.
            # We will process in chunks of `convert_batch_size` to manage memory.
            
            # Note: The original pipeline had nested batching or something specific. 
            # I'll stick to a simple loop: Convert X pages, process them, clear memory.
            
            # Actually, let's use the user's batch params:
            # batch_size: for embedding generation (GPU limit)
            # convert_batch_size: for PDF conversion (RAM limit)
            
            pass # We will implement the loop below
        
        # Implementation of processing loop
        # We iterate through pages in chunks of `convert_batch_size`
        current_page = 1 # 1-based index for pdf2image
        pages_processed = 0
        
        with tqdm(total=total_pages, desc="Processing Pages") as pbar:
            while current_page <= total_pages:
                end_page = min(current_page + convert_batch_size - 1, total_pages)
                
                # Convert
                try:
                    images = convert_from_path(
                        saved_pdf_path, 
                        first_page=current_page, 
                        last_page=end_page
                    )
                except Exception as e:
                    print(f"Error converting pages {current_page}-{end_page}: {e}")
                    current_page = end_page + 1
                    continue
                
                # Save Images Locally
                # Structure: Images/unique_id/unique_id_pageNum.png
                images_dir = os.path.join(config.IMAGES_BASE_PATH, unique_id) # User wanted folder name to be unique_id? 
                # User said: "name of the document should be same as the origianl name along with the unique identifier... this naming should be used for the document in the collection as wel instead of something like tmph..."
                # "Store it as tmph... Now when displaying in the document list this document name should be visible not the temporary name."
                # I will use unique_id for the folder name to avoid conflicts.
                os.makedirs(images_dir, exist_ok=True)
                
                for i, img in enumerate(images):
                    page_num = current_page + i
                    img_path = os.path.join(images_dir, f"{unique_id}_{page_num}.png")
                    img.save(img_path)
                
                # Generate Embeddings in sub-batches
                for i in range(0, len(images), batch_size):
                    batch_imgs = images[i : i + batch_size]
                    
                    with torch.no_grad():
                        processed_batch = self.colpali_processor.process_images(batch_imgs).to(self.colpali_model.device)
                        embeddings = self.colpali_model(**processed_batch)
                    
                    # Upload to Qdrant
                    points = []
                    for j, emb in enumerate(embeddings):
                        page_num = current_page + i + j
                        vector = emb.cpu().float().numpy().tolist()
                        
                        # Payload uses original name for display, but unique ID for reference
                        payload = {
                            "document_name": original_filename, # Display Name
                            "unique_document_id": unique_id,    # Internal ID
                            "page_number": page_num,
                            "timestamp": timestamp,
                            "total_pages": total_pages
                        }
                        
                        points.append(qdrant_models.PointStruct(
                            id=str(uuid.uuid4()), # Unique Point ID
                            vector=vector,
                            payload=payload
                        ))
                    
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                
                # Update progress
                pages_processed += len(images)
                if progress_callback:
                    progress_callback(pages_processed, total_pages)
                
                # Cleanup
                current_page = end_page + 1
                pbar.update(len(images))
                del images
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()

        return unique_id


