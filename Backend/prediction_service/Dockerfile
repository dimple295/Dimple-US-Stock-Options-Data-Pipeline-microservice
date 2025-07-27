FROM python:3.8-slim

WORKDIR /app

COPY prediction_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prediction_service/src/ ./src/

RUN mkdir -p /app/models

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8007"]