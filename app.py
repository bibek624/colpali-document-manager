"""
Streamlit Document Manager Application
Manages Qdrant vector stores and document processing with ColPali
"""

import streamlit as st
import sys
import os

# Add parent directory to path to import from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from qdrant_manager import QdrantManager
import config

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if 'qdrant_manager' not in st.session_state:
    st.session_state.qdrant_manager = QdrantManager(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY
    )

if 'selected_collection' not in st.session_state:
    st.session_state.selected_collection = None

if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Navigation
with st.sidebar:
    st.title("📚 DocManager")
    
    # Test connection status indicator
    if st.session_state.qdrant_manager.test_connection():
        st.caption("🟢 Connected to Qdrant")
    else:
        st.caption("🔴 Disconnected")
        st.warning(f"Check Qdrant at: {config.QDRANT_URL}")
    
    st.markdown("---")
    
    # Modern Navigation
    page = st.radio(
        "Navigation",
        ["Home", "Collections", "Upload", "Manage"],
        index=["Home", "Collections", "Upload", "Manage"].index(st.session_state.get('page', "Home")),
        label_visibility="collapsed",
        format_func=lambda x: f"{'🏠' if x=='Home' else '📁' if x=='Collections' else '📤' if x=='Upload' else '🗑️'} {x}"
    )
    
    # Update session state page if changed via radio
    if page != st.session_state.get('page', "Home"):
        st.session_state.page = page
        st.rerun()

    st.markdown("---")
    
    # Settings in Expander
    with st.expander("Settings", expanded=False):
        st.caption("Configuration")
        st.code(f"URL: {config.QDRANT_URL}", language=None)
        st.code(f"Storage: {config.BASE_STORAGE_PATH}", language=None)

# Main content routing
if st.session_state.page == "Home":
    from views import home_page
    home_page.render(st.session_state.qdrant_manager)

elif st.session_state.page == "Collections":
    from views import collections_page
    collections_page.render(st.session_state.qdrant_manager)

elif st.session_state.page == "Upload":
    from views import upload_page
    upload_page.render(st.session_state.qdrant_manager)

elif st.session_state.page == "Manage":
    from views import manage_page
    manage_page.render(st.session_state.qdrant_manager)

# Minimal Footer
st.markdown("---")
st.caption("Built with Streamlit, ColPali, and Qdrant | Document Vector Store Manager")
