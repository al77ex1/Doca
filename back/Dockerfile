FROM python:3.10-slim

WORKDIR /app

# Set environment variables to prevent Python from writing bytecode and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
    # Don't use PIP_NO_CACHE_DIR=1 to allow pip to use its cache for large packages

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    # Install PyTorch CPU version first (this is the only special case)
    pip install --no-cache-dir torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu && \
    # Then install all requirements
    pip install --no-cache-dir -r requirements.txt && \
    # Verify installations
    python -c "import numpy; print('NumPy version:', numpy.__version__); import torch; print('PyTorch version:', torch.__version__); import huggingface_hub; print('Huggingface Hub version:', huggingface_hub.__version__); from sentence_transformers import SentenceTransformer; print('SentenceTransformer loaded successfully')"

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "server.py"]
