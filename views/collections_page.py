"""
Collections Page - Manage vector store collections
"""

import streamlit as st
from typing import TYPE_CHECKING
import config

if TYPE_CHECKING:
    from qdrant_manager import QdrantManager

def render(qdrant_manager: 'QdrantManager'):
    """Render the collections management page"""
    
    st.title("Collections")
    
    # Create new collection section
    with st.expander("Create New Collection"):
        with st.form("create_collection_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_collection_name = st.text_input("Name", placeholder="my_collection")
            with col2:
                vector_size = st.number_input("Vector Size", value=config.VECTOR_SIZE)
            
            if st.form_submit_button("Create", type="primary"):
                if new_collection_name and new_collection_name.replace("_", "").replace("-", "").isalnum():
                    if qdrant_manager.create_collection(new_collection_name, vector_size):
                        st.success(f"Created '{new_collection_name}'")
                        st.rerun()
                    else:
                        st.error("Failed.")
                else:
                    st.error("Invalid name.")
    
    st.markdown("---")
    
    # List existing collections
    collections = qdrant_manager.list_collections()
    
    if not collections:
        st.info("No collections found.")
        return

    for collection in collections:
        with st.container(border=True):
            stats = qdrant_manager.get_collection_stats(collection)
            docs = stats.get('total_documents', 0) if stats else 0
            points = stats.get('total_points', 0) if stats else 0
            
            # Revised Layout: Info Left, Actions Right
            # Removed Vector Size and Status as requested
            c1, c2 = st.columns([2, 3])
            
            with c1:
                st.subheader(f"📁 {collection}")
                # Combined metrics for cleaner look
                st.caption(f"**{docs}** Documents • **{points:,}** Points")
            
            with c2:
                # Actions pushed to the right
                # Using columns to organize buttons
                # "Upload" and "Manage" buttons are now more visible
                b1, b2, b3 = st.columns([1.5, 1.5, 0.5])
                
                with b1:
                    if st.button("📤 Upload Data", key=f"up_{collection}", use_container_width=True):
                        st.session_state.selected_collection = collection
                        st.session_state.page = "Upload"
                        st.rerun()
                
                with b2:
                    if st.button("🔎 Manage & Search", key=f"man_{collection}", use_container_width=True, type="primary"):
                        st.session_state.selected_collection = collection
                        st.session_state.page = "Manage"
                        st.rerun()
                
                with b3:
                    if st.button("🗑️", key=f"del_{collection}", type="secondary", help="Delete Collection"):
                        st.session_state[f"confirm_{collection}"] = True

            # Confirmation Dialog
            if st.session_state.get(f"confirm_{collection}"):
                st.warning(f"Permanently delete '{collection}'?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Delete", key=f"yes_{collection}", type="primary", use_container_width=True):
                        qdrant_manager.delete_collection(collection)
                        st.session_state[f"confirm_{collection}"] = False
                        st.rerun()
                with col_no:
                    if st.button("Cancel", key=f"no_{collection}", use_container_width=True):
                        st.session_state[f"confirm_{collection}"] = False
                        st.rerun()
