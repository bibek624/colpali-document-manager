import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import config

class MetadataStore:
    """Manages document metadata in a JSON file"""
    
    def __init__(self, storage_path: str = "document_metadata.json"):
        self.storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), storage_path)
        self._ensure_storage()
        
    def _ensure_storage(self):
        """Ensure the JSON file exists"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({"documents": {}}, f)
    
    def _read_data(self) -> Dict:
        """Read data from JSON file"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"documents": {}}
            
    def _write_data(self, data: Dict):
        """Write data to JSON file"""
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=4)
            
    def add_document(self, unique_id: str, metadata: Dict):
        """Add a document to the store"""
        data = self._read_data()
        data["documents"][unique_id] = metadata
        self._write_data(data)
        
    def get_document(self, unique_id: str) -> Optional[Dict]:
        """Get document metadata"""
        data = self._read_data()
        return data["documents"].get(unique_id)
        
    def list_documents(self) -> List[Dict]:
        """List all documents"""
        data = self._read_data()
        return list(data["documents"].values())
        
    def delete_document(self, unique_id: str):
        """Delete a document from the store"""
        data = self._read_data()
        if unique_id in data["documents"]:
            del data["documents"][unique_id]
            self._write_data(data)

