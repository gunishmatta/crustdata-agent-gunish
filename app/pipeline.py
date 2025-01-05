import os

from haystack import Document, Pipeline, component
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from transformers import pipeline
from haystack.document_stores.types import DuplicatePolicy
import uuid


from abc import ABC, abstractmethod
from typing import List

from notion_haystack.notion_exporter import NotionExporter
from haystack import Document
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from huggingface_hub import login  # Import login function
from openai import AzureOpenAI

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
LLAMA2_HOST = os.getenv("LLAMA2_HOST")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

def load_all_data():
    """Loads data from all sources."""
    notion_loader = NotionDataLoader(api_token=NOTION_API_TOKEN,
                                     page_ids=[NOTION_PAGE_ID])
    slack_loader = SlackDataLoader(token=SLACK_TOKEN, channel_id=SLACK_CHANNEL_ID)
    notion_data = notion_loader.load_data()
    slack_data = slack_loader.load_data()
    all_documents = []
    for doc in notion_data + slack_data:
        doc.id = str(uuid.uuid4())
        all_documents.append(doc)

    return all_documents



documents = load_all_data()
document_store = InMemoryDocumentStore()

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(
    instance=SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"), name="doc_embedder"
)
indexing_pipeline.add_component(instance=DocumentWriter(document_store=document_store), name="doc_writer")
indexing_pipeline.connect("doc_embedder.documents", "doc_writer.documents")
indexing_pipeline.run({"doc_embedder": {"documents": documents}})


template = [ChatMessage.from_system("""
You are a Tech Support Engineer, answering questions to people integrating Crustdata's APIs. Use the context provided to answer the question. If the answer involves an API request, provide an example:

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}
Question: {{ question }}
Answer:
""")]

import re


def parse_api_calls(text):
    api_calls = []
    patterns = [
        r"curl --location\s+'?([^']+)'?\s+--header '([^']+)' --header '([^']+)' --header '([^']+)' --data '([^']+)'",
        r"curl --location\s+'?([^']+)'?\s+--header '([^']+)' --header '([^']+)' --header '([^']+)' --query '([^']+)'"
    ]

    for line in text.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                url, auth_header, accept_header, content_type, data_or_query = match.groups()
                method = 'POST' if '--data' in line else 'GET'
                api_calls.append({
                    'method': method,
                    'url': url,
                    'headers': {
                        'Authorization': auth_header,
                        'Accept': accept_header,
                        'Content-Type': content_type if method == 'POST' else None
                    },
                    'data' if method == 'POST' else 'params': eval(data_or_query) if method == 'POST' else data_or_query
                })
    return api_calls


@component
class APIValidationComponent:
    outgoing_edges = 1

    def __init__(self):
        self.required_fields = ["url", "method", "headers"]

    @component.output_types(message=dict)
    def run(self, replies: list[ChatMessage]):
        message = replies[0].content
        api_calls = parse_api_calls(message)

        validated_calls = []
        all_valid = True
        for api_call in api_calls:
            validation_status, fixed_call = self.validate_api_call(api_call)
            validated_calls.append({
                'original': api_call,
                'validated': fixed_call,
                'status': validation_status
            })
            if validation_status != 'valid':
                all_valid = False

        response = {"message": {"text": message}}
        if api_calls and not all_valid:
            response["message"]["api_calls"] = validated_calls

        print(response)
        return response

    def validate_api_call(self, api_call):
        required_headers = ['Authorization', 'Accept']
        if api_call['method'] == 'POST':
            required_headers.append('Content-Type')

        for field in self.required_fields:
            if field not in api_call:
                return "invalid", self.fix_api_call(api_call, f"Missing {field}")

        for header in required_headers:
            if header not in api_call['headers']:
                return "invalid", self.fix_api_call(api_call, f"Missing {header} header")

        if api_call['method'] == 'POST':
            if not isinstance(api_call.get('data', {}), dict):
                return "invalid", self.fix_api_call(api_call, "Invalid data format for POST")

        return "valid", api_call

    def fix_api_call(self, api_call, error):
        if "Missing url" in error:
            api_call['url'] = "default_url"
        elif "Missing method" in error:
            api_call['method'] = "GET"  # Default to GET
        elif "Missing headers" in error:
            api_call['headers'] = {}
        elif "Missing Authorization" in error:
            api_call['headers']['Authorization'] = "Token default_token"
        elif "Missing Accept" in error:
            api_call['headers']['Accept'] = "application/json"
        elif "Missing Content-Type" in error:
            api_call['headers']['Content-Type'] = "application/json"
        elif "Invalid data format for POST" in error:
            api_call['data'] = {"example": "data"}

        api_call['status'] = "fixed"
        return api_call, error

@component
class AzureOpenAIModel:
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )

    @component.output_types(replies=list[ChatMessage])
    def run(self, prompt: list[ChatMessage]):
        """Process the input prompt and generate a response using Azure OpenAI."""
        try:
            messages = [{"role": msg.role, "content": msg.content} for msg in prompt]
            
            response = self.client.chat.completions.create(
                model="gpt-35-turbo",  
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            assistant_reply = response.choices[0].message.content
            return {"replies": [ChatMessage.from_assistant(assistant_reply)]}

        except Exception as e:
            print(f"Error in Azure OpenAI call: {e}")
            return {"replies": [ChatMessage.from_assistant("Sorry, I encountered an error processing your request.")]}

  
rag_pipe = Pipeline()
rag_pipe.add_component("embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
rag_pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
rag_pipe.add_component("prompt_builder", ChatPromptBuilder(template=template))
rag_pipe.add_component("llm", AzureOpenAIModel())
rag_pipe.add_component("api_validator", APIValidationComponent())

rag_pipe.connect("embedder.embedding", "retriever.query_embedding")
rag_pipe.connect("retriever", "prompt_builder.documents")
rag_pipe.connect("prompt_builder.prompt", "llm.prompt")
rag_pipe.connect("llm.replies", "api_validator.replies")
