from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder)
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.retrievers.qdrant import \
    QdrantEmbeddingRetriever

from app.ai.ai import AzureOpenAIModel
from app.ai.api_validation import APIValidationComponent
from app.ai.document_store import QdrantSingleton
from app.ai.load_data import load_all_data


class DataLoaderSingleton:
    _documents = None

    @classmethod
    def get_documents(cls):
        if cls._documents is None:
            cls._documents = load_all_data()
        return cls._documents

documents = DataLoaderSingleton.get_documents()

document_store = QdrantSingleton.get_instance()

# Indexing pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_component(
    instance=SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"),
    name="doc_embedder"
)
indexing_pipeline.add_component(
    instance=DocumentWriter(document_store=document_store),
    name="doc_writer"
)
indexing_pipeline.connect("doc_embedder.documents", "doc_writer.documents")
indexing_pipeline.run({"doc_embedder": {"documents": documents}})

# Create chat prompt template
template = [ChatMessage.from_system("""
You are a Tech Support Engineer, answering questions about Crustdata's APIs. Use the provided context to answer the question. If applicable, include an API request example.
Context: {{ documents | map(attribute='content') | join("\n") }}
Question: {{ question }}
Answer:
""")]

# Create the RAG pipeline
rag_pipe = Pipeline()
embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
retriever = QdrantEmbeddingRetriever(document_store=document_store, top_k=1)
prompt_builder = ChatPromptBuilder(template=template)
llm = AzureOpenAIModel()
api_validator = APIValidationComponent()

# Add components to the pipeline
rag_pipe.add_component("embedder", embedder)
rag_pipe.add_component("retriever", retriever)
rag_pipe.add_component("prompt_builder", prompt_builder)
rag_pipe.add_component("llm", llm)
rag_pipe.add_component("api_validator", api_validator)

# Connect components
rag_pipe.connect("embedder.embedding", "retriever.query_embedding")
rag_pipe.connect("retriever", "prompt_builder.documents")
rag_pipe.connect("prompt_builder.prompt", "llm.prompt")
rag_pipe.connect("llm.replies", "api_validator.replies")


class RagPipeSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = rag_pipe
        return cls._instance

