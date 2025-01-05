from abc import ABC, abstractmethod
from typing import List

from notion_haystack.notion_exporter import NotionExporter
from haystack import Document
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class DataLoader(ABC):
    """Abstract base class for loading data from different sources."""

    @abstractmethod
    def load_data(self) -> List[Document]:
        """Loads data from the specified source."""
        pass

class NotionDataLoader(DataLoader):
    """Loads data from Notion."""

    def __init__(self, api_token, page_ids):
        self.exporter = NotionExporter(api_token=api_token)
        self.page_ids = page_ids

    def load_data(self) -> List[Document]:
        exported_pages = self.exporter.run(page_ids=self.page_ids)
        return exported_pages['documents']


class SlackDataLoader(DataLoader):
    """Loads data from Slack."""

    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.client = WebClient(token=self.token)

    def load_data(self) -> List[Document]:
        """Loads conversations from a Slack channel and creates Document objects."""
        conversations = []
        try:
            result = self.client.conversations_history(channel=self.channel_id)
            messages = result['messages']
            while result['has_more']:
                result = self.client.conversations_history(
                    channel=self.channel_id,
                    oldest=messages[-1]['ts']
                )
                messages.extend(result['messages'])

            for i in range(len(messages) - 1):
                if messages[i]['type'] == 'message' and messages[i+1]['type'] == 'message':
                    question = messages[i]['text']
                    answer = messages[i+1]['text']
                    conversation = f"**Question:** {question}\n**Answer:** {answer}"
                    conversations.append(Document(content=conversation, meta={'source': 'slack'}))

        except SlackApiError as e:
            print(f"Error fetching conversations from Slack: {e}")
            return []

        return conversations
