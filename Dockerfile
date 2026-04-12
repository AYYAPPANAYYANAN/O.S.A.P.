FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ✅ THE FIX: disable hash checking + trust the hosts
# ✅ THE FIX: Increase timeout for large packages and trust the hosts
RUN pip install \
    --no-cache-dir \
    --timeout=1000 \
    --retries=10 \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --trusted-host pypi.python.org \
    -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]