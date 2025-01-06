import logging
import os
import re
import threading

from flask import Flask, jsonify, request
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app import Config
from app.ai.api_validation import parse_api_calls
from app.ai.pipeline import APIValidationComponent, rag_pipe

app = Flask(__name__)

slack_client = WebClient(token=Config.SLACK_TOKEN)

slack_app = App(token=Config.SLACK_TOKEN)

ALLOWED_CHANNELS = ["C0878Q5GAMB"]
# ALLOWED_USERS = ["user1", "user2"]

ERROR_MISSING_QUESTION = "Question is required."
ERROR_MISSING_MESSAGE = "Message is required."
ERROR_INTERNAL_SERVER = "An internal error occurred."


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles user questions and returns answers from the LLM agent.
    """
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": ERROR_MISSING_QUESTION}), 400

    try:
        logging.info(f"Received question: {question}")
        response = rag_pipe.run({
            "embedder": {"text": question},
            "prompt_builder": {"question": question}
        })
        api_validator_response = response.get("api_validator", {})
        response_text = api_validator_response.get("message", {}).get("text", "Unable to process your request.")
        return jsonify({"question": question, "answer": response_text}), 200
    except Exception as e:
        logging.error(f"Error in /chat: {e}")
        return jsonify({"error": ERROR_INTERNAL_SERVER, "details": str(e)}), 500


@app.route('/validate-api', methods=['POST'])
def validate_api():
    """
    Validates API calls extracted from user input.
    """
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": ERROR_MISSING_MESSAGE}), 400

    try:
        logging.info(f"Received message for API validation: {message}")
        api_calls = parse_api_calls(message)
        validation_results = []

        for api_call in api_calls:
            validation_status, fixed_call = APIValidationComponent().validate_api_call(api_call)
            validation_results.append({
                "original": api_call,
                "validated": fixed_call,
                "status": validation_status
            })

        return jsonify({"api_calls": validation_results}), 200
    except Exception as e:
        logging.error(f"Error in /validate-api: {e}")
        return jsonify({"error": ERROR_INTERNAL_SERVER, "details": str(e)}), 500


# Use the correct app instance for Slack event handling
@slack_app.event("app_mention")
def handle_mention(body, logger):
    try:
        event = body["event"]
        channel_id = event["channel"]
        user_id = event["user"]
        text = event["text"]

        # Clean the incoming text
        cleaned_text = re.sub(r'<[^>]*>', '', text)
        logging.info(f"Incoming mention in channel {channel_id} from user {user_id}: {cleaned_text}")

        # Channel and User Filtering
        if channel_id not in ALLOWED_CHANNELS:
            logging.info(f"Channel {channel_id} is not allowed. Ignoring.")
            return
        # Check for allowed users, disabled it for purpose.
        # if user_id not in ALLOWED_USERS:
        #     logging.info(f"User {user_id} is not allowed. Ignoring.")
        #     return

        response = rag_pipe.run({
            "embedder": {"text": cleaned_text},
            "prompt_builder": {"question": cleaned_text}
        })

        api_validator_response = response.get("api_validator", {})
        message = api_validator_response.get("message", {})
        response_text = message.get("text", "Unable to process your request.")
        logging.info(f"Agent response: {response_text}")

        slack_client.chat_postMessage(channel=channel_id, text=response_text)

    except SlackApiError as e:
        logging.error(f"Error posting message to Slack: {e.response['error']}")
    except Exception as e:
        logging.error(f"Unexpected error while processing Slack event: {e}")


def start_flask():
    app.run(host='0.0.0.0', port=5001)


def start_slack_bot():
    SocketModeHandler(slack_app, Config.SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    slack_thread = threading.Thread(target=start_slack_bot)

    flask_thread.start()
    slack_thread.start()

    flask_thread.join()
    slack_thread.join()
