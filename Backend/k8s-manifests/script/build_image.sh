#!/bin/bash

# Base path to the directory where all service folders are
BASE_PATH="../../"
DOCKER_HUB_USERNAME="hdm08"

services=(
  # "data_collector_service"
  # "data_processor_service"
  # "database_writer_service"
  "file_writer_service"
  "data_api_service"
)

# Creates both local image and push to docker hub
for service in "${services[@]}"; do
  echo "📦 Building and pushing: $service"
  docker buildx build \
    --platform linux/arm64 \
    -t ${DOCKER_HUB_USERNAME}/${service}_arm1 \
    --push \
    "${BASE_PATH}${service}"
done

# Creates only local image 
# for service in "${services[@]}"; do
#   echo "📦 Building locally: $service"
  # docker buildx build \
  #   --platform linux/arm64 \
  #   -t hdm08/database_writer_service_arm \
  #   --push \
  #   "${BASE_PATH}database_writer_service"
# # done


# for service in "${services[@]}"; do
#   echo "📦 Building and pushing: $service"
#   docker buildx build \
#     --platform linux/arm64 \
#     -t ${DOCKER_HUB_USERNAME}/${service}_arm \
#     --load \
#     "${BASE_PATH}${service}"
# done