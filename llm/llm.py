from flask import Flask, request, jsonify
from transformers import LlamaForCausalLM, LlamaTokenizer

app = Flask(__name__)

# Load model and tokenizer
model_path = "./model"
tokenizer = LlamaTokenizer.from_pretrained(model_path)
model = LlamaForCausalLM.from_pretrained(model_path)
model.eval()

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.json.get("prompt", "")
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"], max_length=150, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=11434)
