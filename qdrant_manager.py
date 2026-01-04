"""
Qdrant Manager Module
Handles all interactions with the Qdrant vector database including:
- Collection management (list, create, delete)
- Document management (list, delete by document)
- Point operations
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from typing import List, Dict, Optional
import os


class QdrantManager:
    """Manager class for Qdrant operations"""
    
    def __init__(self, url: str = "http://localhost:6333", api_key: Optional[str] = None):
        """Initialize Qdrant client
        
        Args:
            url: Qdrant server URL (default: http://localhost:6333)
            api_key: Optional API key for authentication
        """
        self.client = QdrantClient(url=url, api_key=api_key)
        
    def test_connection(self) -> bool:
        """Test connection to Qdrant server
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """Get list of all collections
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """Get detailed information about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection info or None if error
        """
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status,
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return None
    
    def create_collection(self, collection_name: str, vector_size: int = 128) -> bool:
        """Create a new collection with multivector configuration for ColPali
        
        Args:
            collection_name: Name for the new collection
            vector_size: Size of the vectors (default: 128 for ColQwen2.5)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if collection already exists
            if collection_name in self.list_collections():
                print(f"Collection '{collection_name}' already exists")
                return False
            
            # Configure vector parameters for ColPali multivector support
            vector_params = qdrant_models.VectorParams(
                size=vector_size,
                distance=qdrant_models.Distance.COSINE,
                multivector_config=qdrant_models.MultiVectorConfig(
                    comparator=qdrant_models.MultiVectorComparator.MAX_SIM
                ),
            )
            
            self.client.create_collection(
                collection_name=collection_name,
                on_disk_payload=True,
                optimizers_config=qdrant_models.OptimizersConfigDiff(
                    indexing_threshold=100
                ),
                vectors_config=vector_params,
            )
            print(f"Created collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name)
            print(f"Deleted collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
    
    def list_documents_in_collection(self, collection_name: str) -> List[Dict]:
        """Get list of unique documents in a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of dictionaries with document information
        """
        try:
            # Scroll through all points and collect unique documents
            documents = {}
            offset = None
            
            while True:
                records, offset = self.client.scroll(
                    collection_name=collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                
                if not records:
                    break
                
                for record in records:
                    payload = record.payload
                    unique_doc_id = payload.get("unique_document_id")
                    
                    if unique_doc_id and unique_doc_id not in documents:
                        documents[unique_doc_id] = {
                            "unique_document_id": unique_doc_id,
                            "document_name": payload.get("document_name", "Unknown"),
                            "total_pages": payload.get("total_pages", 0),
                            "timestamp": payload.get("timestamp", ""),
                        }
                
                if offset is None:
                    break
            
            return list(documents.values())
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
    
    def delete_document_from_collection(
        self, collection_name: str, unique_document_id: str
    ) -> bool:
        """Delete all points associated with a specific document
        
        Args:
            collection_name: Name of the collection
            unique_document_id: Unique document identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all points with matching unique_document_id
            self.client.delete(
                collection_name=collection_name,
                points_selector=qdrant_models.FilterSelector(
                    filter=qdrant_models.Filter(
                        must=[
                            qdrant_models.FieldCondition(
                                key="unique_document_id",
                                match=qdrant_models.MatchValue(value=unique_document_id),
                            )
                        ]
                    )
                ),
            )
            print(f"Deleted document '{unique_document_id}' from collection '{collection_name}'")
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_collection_stats(self, collection_name: str) -> Optional[Dict]:
        """Get statistics about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with statistics or None if error
        """
        try:
            info = self.client.get_collection(collection_name)
            documents = self.list_documents_in_collection(collection_name)
            
            return {
                "total_points": info.points_count,
                "total_documents": len(documents),
                "status": info.status,
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return None





