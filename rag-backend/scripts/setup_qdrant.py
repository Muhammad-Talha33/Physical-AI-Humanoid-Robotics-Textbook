"""Initialize Qdrant collection for book embeddings."""
import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import settings


def setup_qdrant():
    """Create and configure Qdrant collection."""
    print(f"Connecting to Qdrant at {settings.qdrant_url}...")

    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    collection_name = settings.qdrant_collection_name

    # Check if collection already exists
    try:
        collections = client.get_collections().collections
        if any(col.name == collection_name for col in collections):
            print(f"Collection '{collection_name}' already exists.")
            response = input("Do you want to recreate it? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                client.delete_collection(collection_name)
                print(f"Deleted existing collection '{collection_name}'")
            else:
                print("Keeping existing collection.")
                return
    except Exception as e:
        print(f"Error checking collections: {e}")

    # Create new collection
    # Using 1536 dimensions for text-embedding-3-small or text-embedding-ada-002
    # Adjust if using different model
    vector_size = 1536 if "ada-002" in settings.openai_embedding_model else 1536

    print(f"Creating collection '{collection_name}' with vector size {vector_size}...")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

    print(f"Collection '{collection_name}' created successfully!")
    print(f"  - Vector size: {vector_size}")
    print(f"  - Distance metric: Cosine")

    # Verify collection
    info = client.get_collection(collection_name)
    print(f"\nCollection info:")
    print(f"  - Vectors count: {info.points_count}")
    print(f"  - Status: {info.status}")


if __name__ == "__main__":
    try:
        setup_qdrant()
    except Exception as e:
        print(f"Error setting up Qdrant: {e}")
        sys.exit(1)
