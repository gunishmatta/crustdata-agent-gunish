# Base image for serving LLaMA2
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Set working directory
WORKDIR /llama2

# Install required Python libraries
RUN pip install --no-cache-dir flask transformers accelerate

# Copy model files
COPY model /llama2/model

# Copy LLaMA2 server script
COPY llm.py /llm

# Expose model serving port
EXPOSE 11434

# Run the model server
CMD ["python", "llm.py"]
