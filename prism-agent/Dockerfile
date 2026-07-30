FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir scapy httpx pydantic structlog psutil scikit-learn joblib pytest

COPY agent/ ./agent
COPY rules/ ./rules

CMD ["python", "-m", "agent.main"]
