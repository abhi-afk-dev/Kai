FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g @modelcontextprotocol/server-github

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]