#!/bin/bash

# Base path to the directory where all service folders are
BASE_PATH="../../"
DOCKER_HUB_USERNAME = "hdm08"

services=(
  "airflow_scheduler_service"
  "data_collector_service"
  "data_processor_service"
  "database_writer_service"
  "file_writer_service"
  "data_api_service"
)

for service in "${services[@]}"; do
  echo "📦 Building and pushing: $service"
  docker buildx build \
    --platform linux/amd64 \
    -t ${DOCKER_HUB_USERNAME}/${service} \
    --push \
    "${BASE_PATH}${service}"
done
