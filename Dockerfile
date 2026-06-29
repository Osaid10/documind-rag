FROM python:3.11-slim

WORKDIR /app

# System deps for building native extensions (chromadb, torch, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer-cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ .

# Ensure storage directory exists inside the image
RUN mkdir -p /app/storage/chroma_db

EXPOSE 8501

CMD ["streamlit", "run", "main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
