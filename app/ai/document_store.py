from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


class QdrantSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if QdrantSingleton._instance is None:
            QdrantSingleton._instance = QdrantDocumentStore(
                embedding_dim=384,
                similarity="cosine"
            )
        return QdrantSingleton._instance


from qdrant_client import QdrantClient


class QdrantClientSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if QdrantClientSingleton._instance is None:
            QdrantClientSingleton._instance = QdrantClient("http://localhost:6333")
        return QdrantClientSingleton._instance


# Usage
client = QdrantClientSingleton.get_instance()
