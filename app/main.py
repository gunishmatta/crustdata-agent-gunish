from flask import Flask, request, jsonify

from app.pipeline import APIValidationComponent, parse_api_calls, rag_pipe

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles user questions and returns answers from the LLM agent.
    Request body:
    {
        "question": "Your API question here"
    }
    """
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = rag_pipe.run({
            "embedder": {"text": question},
            "prompt_builder": {"question": question}
        })
        api_validator_response = response.get("api_validator", {})
        response_text = api_validator_response.get("message", {}).get("text", "Unable to process your request.")

        return jsonify({"question": question, "answer": response_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/validate-api', methods=['POST'])
def validate_api():
    """
    Validates API calls extracted from user input.
    Request body:
    {
        "message": "curl command or text containing API calls"
    }
    """
    data = request.json
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
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
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
