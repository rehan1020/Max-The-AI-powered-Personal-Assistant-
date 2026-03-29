"""Vector store for semantic memory search using chromadb."""

from pathlib import Path
from typing import Optional

from core.logger import logger

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorStore:
    """Semantic memory using chromadb embeddings."""

    def __init__(self, persist_directory: Path):
        """Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the vector store.
        """
        self._persist_dir = persist_directory
        self._client = None
        self._collection = None

        if not CHROMADB_AVAILABLE:
            logger.warning("chromadb not available, vector memory disabled")
            return

        try:
            self._client = chromadb.PersistentClient(
                path=str(persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name="memory",
                metadata={"description": "Max AI Agent conversation history"}
            )
            logger.info(f"Vector store initialized at {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self._client = None
            self._collection = None

    def add_memory(self, conversation_id: str, text: str) -> bool:
        """Add a conversation to the vector store.
        
        Args:
            conversation_id: Unique ID for the conversation.
            text: The conversation text.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self._collection:
            return False

        try:
            self._collection.add(
                documents=[text],
                ids=[conversation_id]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False

    def search(self, query: str, n_results: int = 3) -> list[str]:
        """Search for relevant past conversations.
        
        Args:
            query: The search query.
            n_results: Number of results to return.
            
        Returns:
            List of relevant conversation texts.
        """
        if not self._collection:
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results
            )
            documents = results.get("documents", [[]])[0]
            return documents
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation from the store.
        
        Args:
            conversation_id: The ID to delete.
            
        Returns:
            True if successful.
        """
        if not self._collection:
            return False

        try:
            self._collection.delete(ids=[conversation_id])
            return True
        except Exception:
            return False

    def count(self) -> int:
        """Get the number of stored memories."""
        if not self._collection:
            return 0
        return self._collection.count()
