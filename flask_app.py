import logging

from flask import Flask, jsonify, request

from app.ai.pipeline import RagPipeSingleton

app = Flask(__name__)

ERROR_MISSING_QUESTION = "Question is required."
ERROR_INTERNAL_SERVER = "An internal error occurred."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": ERROR_MISSING_QUESTION}), 400

    try:
        logging.info(f"Received question: {question}")
        response = RagPipeSingleton.get_instance().run({
            "embedder": {"text": question},
            "prompt_builder": {"question": question}
        })
        api_validator_response = response.get("api_validator", {})
        response_text = api_validator_response.get("message", {}).get("text", "Unable to process your request.")
        return jsonify({"question": question, "answer": response_text}), 200
    except Exception as e:
        logging.error(f"Error in /chat: {e}")
        return jsonify({"error": ERROR_INTERNAL_SERVER, "details": str(e)}), 500