FROM python:3.11-slim
WORKDIR /app

COPY services/streamlit_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/streamlit_app/app.py .

ENV EVITO_API_URL=http://localhost:8081
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
