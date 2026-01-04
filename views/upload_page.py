"""
Upload Page - Upload and process documents
"""

import streamlit as st
from typing import TYPE_CHECKING
import os
import sys
import tempfile
import config
from document_processor import DocumentProcessor

if TYPE_CHECKING:
    from qdrant_manager import QdrantManager

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def render(qdrant_manager: 'QdrantManager'):
    """Render the document upload page"""
    
    st.title("Upload Document")
    
    # Get collections
    collections = qdrant_manager.list_collections()
    
    if not collections:
        st.warning("No collections found.")
        if st.button("Create Collection", type="primary"):
            st.session_state.page = "Collections"
            st.rerun()
        return
    
    # Centered layout for focus
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        with st.container(border=True):
            st.subheader("Select Target")
            # Collection Selection
            default_idx = 0
            if st.session_state.get('selected_collection') in collections:
                default_idx = collections.index(st.session_state.selected_collection)
            
            selected_collection = st.selectbox(
                "Collection",
                collections,
                index=default_idx,
                label_visibility="collapsed"
            )
            st.session_state.selected_collection = selected_collection
            
            # Tiny stat
            stats = qdrant_manager.get_collection_stats(selected_collection)
            if stats:
                st.caption(f"Contains {stats.get('total_documents', 0)} documents")

        st.markdown("") # Spacer

        with st.container(border=True):
            st.subheader("Upload PDF(s)")
            uploaded_files = st.file_uploader(
                "Choose file(s)",
                type=['pdf'],
                accept_multiple_files=True,
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                st.info(f"Ready: {len(uploaded_files)} file(s) selected")
                for uploaded_file in uploaded_files:
                    st.caption(f"📄 {uploaded_file.name} ({uploaded_file.size / (1024 * 1024):.1f} MB)")
        
        st.markdown("") # Spacer

        with st.expander("Advanced Configuration"):
            batch_size = st.slider(
                "Embedding Batch Size",
                min_value=1, max_value=16, value=config.DEFAULT_BATCH_SIZE
            )
            convert_batch_size = st.slider(
                "PDF Conversion Batch Size",
                min_value=5, max_value=50, value=config.DEFAULT_CONVERT_BATCH_SIZE
            )
        
        if uploaded_files:
            if st.button("Start Processing", type="primary", use_container_width=True):
                # Initialize processor once for all documents
                processor = DocumentProcessor(selected_collection)
                
                # Track overall progress
                overall_container = st.container()
                with overall_container:
                    st.subheader(f"Processing {len(uploaded_files)} document(s)...")
                    overall_progress = st.progress(0, text="Starting...")
                
                successful_uploads = []
                failed_uploads = []
                
                # Process each file
                for file_idx, uploaded_file in enumerate(uploaded_files):
                    # Save uploaded file to temp
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        # Create a status container for this document
                        status_container = st.status(
                            f"Processing {uploaded_file.name}...", 
                            expanded=True
                        )
                        with status_container:
                            st.write(f"📄 Document {file_idx + 1} of {len(uploaded_files)}")
                            
                            # Create a placeholder for page progress
                            progress_placeholder = st.empty()
                            
                            # Process document with progress callback
                            unique_id = processor.process_document(
                                temp_file_path=tmp_file_path,
                                original_filename=uploaded_file.name,
                                batch_size=batch_size,
                                convert_batch_size=convert_batch_size,
                                progress_callback=lambda current, total: progress_placeholder.write(
                                    f"📊 Pages processed: {current}/{total}"
                                )
                            )
                            
                            st.write("✅ Complete!")
                            status_container.update(
                                label=f"✅ {uploaded_file.name}", 
                                state="complete", 
                                expanded=False
                            )
                        
                        successful_uploads.append(uploaded_file.name)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {e}")
                        failed_uploads.append((uploaded_file.name, str(e)))
                    finally:
                        try:
                            os.unlink(tmp_file_path)
                        except:
                            pass
                    
                    # Update overall progress
                    progress_pct = (file_idx + 1) / len(uploaded_files)
                    overall_progress.progress(
                        progress_pct, 
                        text=f"Completed {file_idx + 1}/{len(uploaded_files)} documents"
                    )
                
                # Show final summary
                st.markdown("---")
                if successful_uploads:
                    st.success(f"✅ Successfully processed {len(successful_uploads)} document(s):")
                    for name in successful_uploads:
                        st.write(f"  • {name}")
                
                if failed_uploads:
                    st.error(f"❌ Failed to process {len(failed_uploads)} document(s):")
                    for name, error in failed_uploads:
                        st.write(f"  • {name}: {error}")
                
                if st.button("Upload More Documents"):
                    st.rerun()
