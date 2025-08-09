#!/bin/bash

# Base path to the directory where all service folders are
BASE_PATH="../../"
DOCKER_HUB_USERNAME="hdm08"

services=(
  "data_collector_service"
  "data_processor_service"
  "database_writer_service"
  # "file_writer_service"
  "data_api_service"
)
# #_____________________Local image___________________________________________________

for service in "${services[@]}"; do
  echo "📦 Building and pushing: $service"
  docker buildx build \
    --platform linux/arm64 \
    -t ${DOCKER_HUB_USERNAME}/${service}_arm10 \
    --load \
    "${BASE_PATH}Backend/${service}"
done

# #-----File writer with amd architecture
docker buildx build \
    --platform linux/amd64 \
    -t hdm08/file_writer_service_arm10 \
    --load  \
    "${BASE_PATH}Backend/file_writer_service"

# #-----Frontend
docker buildx build \
    --platform linux/arm64 \
    -t ${DOCKER_HUB_USERNAME}/frontend_arm10 \
    --load \
    "${BASE_PATH}Frontend/Stock_Analysis_Frontend"

# #________________________docker hub________________________________________________

for service in "${services[@]}"; do
  echo "📦 Building and pushing: $service"
  docker buildx build \
    --platform linux/arm64 \
    -t ${DOCKER_HUB_USERNAME}/${service}_arm10 \
    --push \
    "${BASE_PATH}Backend/${service}"
done

# #-----File writer with amd architecture
docker buildx build \
    --platform linux/amd64 \
    -t hdm08/file_writer_service_arm10 \
    --push  \
    "${BASE_PATH}Backend/file_writer_service"

# #-----Frontend
docker buildx build \
    --platform linux/arm64 \
    -t ${DOCKER_HUB_USERNAME}/frontend_arm10 \
    --push \
    "${BASE_PATH}Frontend/Stock_Analysis_Frontend"