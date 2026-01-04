"""
Home Page - Dashboard view with overview statistics
"""

import streamlit as st
from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from qdrant_manager import QdrantManager


def render(qdrant_manager: 'QdrantManager'):
    """Render the home page with dashboard statistics"""
    
    st.title("Dashboard")
    st.caption("Welcome to Document Manager")
    
    # Get all collections
    collections = qdrant_manager.list_collections()
    
    if not collections:
        st.info("No collections found. Start by creating one.")
        if st.button("Create Collection"):
            st.session_state.page = "Collections"
            st.rerun()
        return

    # Prepare data for a clean table
    data = []
    total_docs = 0
    total_points = 0
    
    for collection in collections:
        stats = qdrant_manager.get_collection_stats(collection)
        if stats:
            docs = stats.get('total_documents', 0)
            points = stats.get('total_points', 0)
            total_docs += docs
            total_points += points
            
            data.append({
                "Collection Name": collection,
                "Documents": docs,
                "Vector Points": f"{points:,}",
                "Status": stats.get('status', 'Unknown')
            })
    
    # Summary Metrics (Simple)
    m1, m2 = st.columns(2)
    m1.metric("Total Documents", total_docs)
    m2.metric("Total Collections", len(collections))
    
    st.markdown("### Active Collections")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Collection Name": st.column_config.TextColumn("Name", width="medium"),
                "Documents": st.column_config.NumberColumn("Docs", format="%d"),
                "Vector Points": st.column_config.TextColumn("Vectors"),
                "Status": st.column_config.TextColumn("Status")
            }
        )
    else:
        st.caption("No data available.")

    st.markdown("")
    st.caption("Use the sidebar to manage collections or upload documents.")
