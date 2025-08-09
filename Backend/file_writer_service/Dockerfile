FROM python:3.9-slim

WORKDIR /app 
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev curl gnupg netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .
EXPOSE 8003

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "file_writer_service.wsgi:application"]

