# Generalized Dockerfile for aria-node-base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Install libpcap for Scapy
RUN apt-get update && apt-get install -y libpcap-dev && rm -rf /var/lib/apt/lists/*

# Exclude .pem files from being copied into the image
RUN find . -name "*.pem" -delete

ENV PYTHONPATH=/app:/app/net:/app/proto
ENV DASHBOARD_URL 172.17.0.2
# Set the default command to run the node
CMD ["python3", "node.py"]
