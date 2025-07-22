# Set your Docker Hub username (or other registry)
REGISTRY_USER="hdm08"
TAG="latest"

docker compose build
# Build all images using Docker Compose
# cd ../../
# cd data_collector_service/
# docker buildx build --platform linux/amd64 -t hdm08/backend-data-collector --push .
# cd ..

# cd  data_processor_service/
# docker buildx build --platform linux/amd64 -t hdm08/backend-data-processor --push .
# cd ..

# cd  database_writer_service/
# docker buildx build --platform linux/amd64 -t hdm08/backend-database-writer --push .
# cd ..

# cd  file_writer_service/ 
# docker buildx build --platform linux/amd64 -t hdm08/backend-file-writer --push .
# cd ..

# cd  data_api_service/   
# docker buildx build --platform linux/amd64 -t hdm08/backend-data-api-service --push .
# cd ..

# List of service image names
services=(
  backend-airflow
  backend-data-collector
  backend-data-processor
  backend-database-writer
  backend-file-writer
  backend-data-api-service
)

# Tag and push each image
for service in "${services[@]}"
do

  IMAGE_NAME="$REGISTRY_USER/$service:$TAG"
    # IMAGE_NAME="$REGISTRY_USER/backend-file-writer:$TAG"

  # echo "Tagging image: $service -> $IMAGE_NAME"
  # docker tag $service $IMAGE_NAME
  # docker tag backend-file-writer "$REGISTRY_USER/$IMAGE_NAME"

  echo "Pushing image: $IMAGE_NAME"
  docker push $IMAGE_NAME
done

echo "✅ All images built and pushed successfully!"
