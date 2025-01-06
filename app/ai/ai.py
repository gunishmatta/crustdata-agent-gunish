from haystack import component
from haystack.components.generators import AzureOpenAIGenerator
from haystack.dataclasses import ChatMessage

from app.config import Config


@component
class AzureOpenAIModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AzureOpenAIModel, cls).__new__(cls)
            cls._instance.generator = AzureOpenAIGenerator(
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_key=Config.AZURE_OPENAI_API_KEY,
                azure_deployment="gpt-4-32k"
            )
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    @component.output_types(replies=list[ChatMessage])
    def run(self, prompt: list[ChatMessage]):
        """Process the input prompt and generate a response using Azure OpenAI Generator."""
        try:
            response = self.generator.run(prompt = " ".join([message.content for message in prompt]))
            return {"replies": response['replies']}

        except Exception as e:
            print(f"Error in Azure OpenAI call: {e}")
            return {"replies": [ChatMessage.from_assistant("Sorry, I encountered an error processing your request.")]}