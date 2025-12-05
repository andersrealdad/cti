FROM python:3.11-slim
WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application
COPY evito_api_server.py .
COPY risk_bot.py* ./ 2>/dev/null || true
# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8081/health')"
EXPOSE 8081
CMD ["python", "evito_api_server.py"]
