from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from app import Config


class QdrantSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if QdrantSingleton._instance is None:
            QdrantSingleton._instance = QdrantDocumentStore(
                embedding_dim=384,
                similarity="cosine",
                host="localhost"
            )
        return QdrantSingleton._instance


from qdrant_client import QdrantClient


class QdrantClientSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if QdrantClientSingleton._instance is None:
            QdrantClientSingleton._instance = QdrantClient(Config.QDRANT_URL)
        return QdrantClientSingleton._instance


