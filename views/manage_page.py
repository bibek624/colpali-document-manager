"""
Manage Page - View and delete documents from collections
"""

import streamlit as st
from typing import TYPE_CHECKING
import os
import shutil
import base64
import urllib.parse
import config
from metadata_store import MetadataStore

# Initialize metadata store
metadata_store = MetadataStore()

if TYPE_CHECKING:
    from qdrant_manager import QdrantManager

def render(qdrant_manager: "QdrantManager"):
    """Render the document management page"""

    st.title("Manage Documents")

    # Get collections
    collections = qdrant_manager.list_collections()

    if not collections:
        st.warning("No collections found.")
        return

    # Collection selection
    col_sel_1, col_sel_2 = st.columns([2, 1])
    with col_sel_1:
        default_idx = 0
        if st.session_state.get("selected_collection") in collections:
            default_idx = collections.index(st.session_state.selected_collection)

        selected_collection = st.selectbox(
            "Select Collection",
            collections,
            index=default_idx
        )
        st.session_state.selected_collection = selected_collection
    
    st.divider()

    # Get documents from Qdrant
    qdrant_docs = qdrant_manager.list_documents_in_collection(selected_collection)
    
    if not qdrant_docs:
        st.info("No documents in this collection.")
        if st.button("Upload Document", type="primary"):
            st.session_state.page = "Upload"
            st.rerun()
        return

    # Search
    search_term = st.text_input("🔍 Search Documents", placeholder="Filter by name...")
    
    filtered_documents = qdrant_docs
    if search_term:
        filtered_documents = [
            doc for doc in qdrant_docs 
            if search_term.lower() in doc["document_name"].lower()
        ]
        st.caption(f"Found {len(filtered_documents)} matches")

    # List Header
    st.subheader("Documents List")

    for idx, doc in enumerate(filtered_documents, 1):
        # Merge with local metadata if available
        unique_id = doc["unique_document_id"]
        meta = metadata_store.get_document(unique_id)
        
        display_name = doc["document_name"]
        pdf_path = None
        
        if meta:
            if "original_name" in meta:
                display_name = meta["original_name"]
            if "pdf_path" in meta:
                pdf_path = meta["pdf_path"]
        
        # Fallback for PDF path if not in metadata but exists on disk
        if not pdf_path:
             potential_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Documents", f"{unique_id}.pdf")
             if os.path.exists(potential_path):
                 pdf_path = potential_path

        with st.container(border=True):
            # Header
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"#### 📄 {display_name}")
                st.caption(f"ID: `{unique_id}` | Pages: {doc['total_pages']} | Date: {doc['timestamp']}")
                
                # PDF Link
                if pdf_path and os.path.exists(pdf_path):
                     # Construct static URL relative to the app
                     # Files in 'static' at root are served at 'app/static/...'
                     # We symlinked Documents to static/documents
                     # URL encode the filename to handle spaces
                     encoded_filename = urllib.parse.quote(f"{unique_id}.pdf")
                     pdf_url = f"/app/static/documents/{encoded_filename}"
                     
                     # Expander for inline viewing
                     with st.expander("📄 View Document", expanded=False):
                        if os.path.exists(pdf_path):
                             # Use static URL for iframe as well to avoid base64 overhead
                             pdf_display = f'<iframe src="{pdf_url}" width="100%" height="800" type="application/pdf"></iframe>'
                             st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.caption("PDF file not available")

            with c2:
                if st.button("🗑️ Delete", key=f"del_btn_{idx}", type="secondary", use_container_width=True):
                    st.session_state[f"confirm_delete_doc_{unique_id}"] = True

            # Delete Confirmation
            if st.session_state.get(f"confirm_delete_doc_{unique_id}", False):
                st.error("Delete this document and all its embeddings?")
                dc1, dc2 = st.columns(2)
                with dc1:
                     if st.button("Yes, Delete", key=f"confirm_yes_doc_{idx}", type="primary", use_container_width=True):
                        delete_document(
                            qdrant_manager,
                            selected_collection,
                            unique_id,
                            doc["document_name"]
                        )
                with dc2:
                     if st.button("Cancel", key=f"confirm_no_doc_{idx}", use_container_width=True):
                        st.session_state[f"confirm_delete_doc_{unique_id}"] = False
                        st.rerun()

def delete_document(qdrant_manager, collection_name, unique_document_id, document_name):
    """Delete a document from the collection and remove its images"""
    
    with st.spinner("Deleting..."):
        # Delete from Qdrant
        if qdrant_manager.delete_document_from_collection(collection_name, unique_document_id):
            
            # Delete images (check both new and old paths)
            paths_to_check = [
                os.path.join(config.IMAGES_BASE_PATH, unique_document_id),
                os.path.join(config.IMAGES_BASE_PATH, document_name)
            ]
            
            for path in paths_to_check:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                    except Exception as e:
                        print(f"Warning: Could not delete images at {path}: {e}")

            # Also delete PDF from Documents folder if exists
            pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Documents", f"{unique_document_id}.pdf")
            if os.path.exists(pdf_path):
                try:
                    os.unlink(pdf_path)
                except:
                    pass

            # Remove from metadata store
            metadata_store.delete_document(unique_document_id)
            
            st.success(f"Deleted document")
            st.session_state[f"confirm_delete_doc_{unique_document_id}"] = False
            st.rerun()
        else:
            st.error("Failed to delete from vector store")
