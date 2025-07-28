# US-Stock-Options-Data-Pipeline-microservice


# Project Overview

This project implements a microservices-based data pipeline to periodically fetch, process, and store U.S. stock market options data. The system is designed to be highly available, resilient, and observable, with data stored in both a database (SQL/NoSQL/Time-series) and as CSV files in an object storage solution. The pipeline uses a public API for data retrieval, employs Kubernetes for orchestration, and integrates Prometheus and Grafana for observability.

# Key Objectives
- Data Ingestion and Processing: Fetch stock options data via a public API, process it, and store it in a database and object storage.
- Microservices Architecture: Implement up to eight microservices, each with at least two instances for high availability.
- High Availability and Load Balancing: Ensure resilience with load balancing and failover mechanisms.
- Observability: Monitor data ingestion, API response times, system health, and data freshness using Prometheus and Grafana.

# System Architecture
The pipeline consists of seven microservices:

1. airflow_scheduler_service: Orchestrates workflows and schedules data collection tasks.
2. data_api_service: Provides API endpoints for external access to processed data.
3. data_collector_service: Fetches raw data from Twelve Data API and yfinance.
4. data_processor_service: Preprocesses and validates raw data.
5. database_writer_service: Stores processed data in Azure SQL and InfluxDB.
6. file_writer_service: Handles file-based data outputs (if applicable).
7. prediction_service: Generates predictions based on processed data.


# Prerequisites
- Azure CLI
- Kubectl
- Helm
- Docker Desktop
- DockerHub account for image storage
- API key for Twelve Data
- Access to a terminal with administrative privileges

# Microservices Details

## Kafka Configuration

Apache Kafka is used for streaming data between services. The configuration is managed in KafkaConfig.py, which defines producer and consumer instances. The following Kafka topics are used, each with 5 partitions for parallel processing:

1. task-queue: For asynchronous, non-blocking API calls.
2. daily-data: Streams daily stock data.
3. 15min-data: Streams real-time (15-minute) stock data.
4. historical-data: Streams historical stock data.
5. option-data: Streams options data.
6. processed-daily-data: Streams processed daily data.
7. processed-15min-data: Streams processed real-time data.
8. processed-historical-data: Streams processed historical data.
9. processed-options-data: Streams processed options data.


## Airflow Scheduler Service


## Data Collector Service

This service fetches raw data from external sources (Twelve Data API and yfinance library) and publishes it to Kafka topics.

Endpoints:
- fetch_daily_data: Fetches daily stock data from Twelve Data API.
- fetch_15min_data: Fetches 15-minute real-time stock data from Twelve Data API.
- fetch_historical_data: Fetches historical stock data from Twelve Data API.
- fetch_option_data: Fetches options data (next 90 days) from yfinance.

1. For fetch_daily_data, fetch_15min_data, and fetch_historical_data:
- Tasks are published to the task-queue Kafka topic for asynchronous processing.
- run_kafka_collector.py consumes tasks and uses multithreading (5 threads) to fetch data for 120 symbols, adhering to Twelve Data API's limit of 8 requests per minute per thread.
- Each thread processes 24 symbols in 3 minutes, fetching data in batches of 8 per minute.
- DataCollector.py (via ThreadedDataCollector) handles parallel data fetching and publishes to respective Kafka topics (daily-data, 15min-data, historical-data).

2. For fetch_option_data:
- Fetches data directly from yfinance (no API limits) in batches of 8 for simplicity.
- OptionDataCollector.py handles data fetching and publishes to the option-data Kafka topic.

## Data Processor Service

This service consumes raw data from Kafka, preprocesses it, and publishes processed data to new Kafka topics.

run_kafka_processor.py:
- Consumes data from daily-data, 15min-data, historical-data, and option-data.
- Creates a worker thread per partition (5 threads per topic) to process data asynchronously.
- Periodically checks for new partitions to start additional worker threads.
- Routes data to specific handlers based on the topic:
    - daily-data → DailyDataProcessor
    - 15min-data → RealTimeDataProcessor
    - historical-data → HistoricalDataProcessor
    - option-data → OptionDataProcessor
- Each handler calls DataPreprocessor, which:
    - Fixes data types.
    - Handles missing values using forward fill and mean value imputation.
    - Removes duplicates.
    - Validates and removes invalid rows.
    - Standardizes formatting.
- Processed data is published to:
    - processed-daily-data
    - processed-15min-data
    - processed-historical-data
    - processed-options-data

## Database Writer Service

This service consumes processed data from Kafka and stores it in databases.

run_kafka_writer.py:
- Consumes data from processed-daily-data, processed-15min-data, processed-historical-data, and processed-options-data.
- Creates a worker thread per partition (5 threads per topic) for asynchronous processing.
- Periodically checks for new partitions to start additional worker threads.
- Routes data to specific handlers based on the topic:
    - processed-daily-data → DailySQLHandler (stores in Azure SQL).
    - processed-15min-data → influxHandler (stores in InfluxDB for real-time data).
    - processed-historical-data → HistoricalSQLHandler (stores in Azure SQL).
    - processed-options-data → OptionDataProcessor (stores in Azure SQL).


## File Writer Service


## Data Api Service


## Prediction Service



## Observability

#### Prometheus: Collects metrics on:


#### Grafana: Dashboards visualize:



# Frontend




# Load Balancing and Resilience
- Load Balancing: Nginx Ingress and Azure Kubernetes LoadBalancer distribute traffic across microservice instances.
- Resilience:
    - Two instances per microservice ensure failover.
    - Database replication maintains data consistency.
    - Object storage (AWS S3) to store data for durability.
    - Kubernetes auto-scaling and self-healing handle instance failures.


# Dependencies
- Data Sources: Tweleve Data, yfinance
- Orchestration & Workflow Management: apache-airflow, docker, kubernetes
- Web Framework & API: django, djangorestframework, gunicorn, django-cors-headers
- Monitoring & Observability: django-prometheus, prometheus, grafana
- Utilities & Environment Management: python-dotenv, six
- Data & Analytics: pandas, numpy, python-dateutil, pytz, scikit-learn, python-ta-lib, torch
- Messaging & Streaming: confluent-kafka, apache kafka
- Databases & Storage: psycopg2-binary, pyodbc, sqlalchemy, pymysql, influxdb-client, azure-SQL, influxDB, AWS-S3
- Cloud & Networking: boto3, nginx-ingress, Azure Load Balancer
- Frontend: Angular

# Scaling and Performance

- Multithreading: Each service uses 5 threads per Kafka topic partition to parallelize data fetching, processing, and writing.
- Kafka Partitions: 5 partitions per topic ensure balanced load distribution.
- API Limits: The data_collector_service respects Twelve Data API's 8 requests per minute limit, processing 120 symbols in 3 minutes across 5 threads i.e 24 symbol per thread.


# Setup Instructions

### Docker Setup:
    - cd Backend
    - configure the environment variable
    - docker compose up --build
    - check the logs in docker desktop

### Kubernetes Setup:

1. Create a Kubernetes Cluster: Navigate to the cluster configuration directory and create a cluster(1 control palne  and 2 worker nodes) using Kind.
    - cd k8s-manifests/cluster
    - kind create cluster --config kind-config.yaml

2. Push the docker images of services to the docker hub
    - Note: If service images are already pushed to DockerHub via CI/CD skip this step
    - cd k8s-manifests/scripts
    - update the DOCKER_HUB_USERNAME in file k8s-manifests/scripts/build_image.sh
    - chmod +x build_image.sh
    - ./build_image.sh


3. Install Helm Packages: Install necessary Helm packages such as Kafka, Prometheus, Grafana, and Nginx Ingress.
    - cd k8s-manifests/scripts
    - chmod +x helm.sh
    - ./helm.sh

4. Apply Manifests: Apply the Kubernetes manifests to deploy services to the cluster.
    - cd k8s-manifests
    - kubectl apply -f manifests    

5. Check Pod and Service Status: Verify the status of pods and services in the cluster.
    - kubectl get pods
    - kubectl get svc

6. Troubleshoot Pod Issues: If any pod fails, check its logs for debugging.
    - kubectl logs <pod-name>
    - Replace <pod-name> with the name of the failing pod.

7. Port Forward a Service: To access a service locally, use port forwarding.
    - kubectl port-forward svc/<service-name> <local-port>:<target-port>
    - Replace <service-name>, <local-port>, and <target-port> with the appropriate values.
    
### Azure Setup

1. Install azure cli: Install the Azure CLI using Homebrew (on macOS/Linux).
    - brew install azure-cli

2. Login to azure: Authenticate with Azure and verify the active account.
    - az login
    - az account show

3. Create Resources Group: Create a resource group for the Kubernetes cluster and load balancer.
    - az group create --name stockPipelineResource --location northeurope

4. Create Azure Kubernetes Cluster: Create an Azure Kubernetes Service (AKS) cluster with 2 worker nodes. Azure manages the control plane.
    - az aks create \
    --resource-group stockPipelineResource \
    --name stockCluster \
    --node-count 2 \
    --node-vm-size Standard_B2s \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --load-balancer-sku standard

5. Configure Local Kubectl: Configure kubectl to manage the Azure cluster locally.
    - az aks get-credentials --resource-group stockPipelineResource --name stockCluster 

6. Verify Cluster Nodes: Check the status of the cluster nodes.
    - kubectl get nodes

7. Kubernetes Secrets: Create a Kubernetes secret to authenticate with DockerHub.
    - kubectl create secret docker-registry dockerhub-secret \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=<docker-username> \
    --docker-password=<docker-token> \
    --docker-email=<docker-email>
    - Replace <docker-username>, <docker-token>, and <docker-email> with your DockerHub credentials.

8. Push the docker images of services to the docker hub
    - Note: If service images are already pushed to DockerHub via CI/CD skip this step
    - cd k8s-manifests/scripts
    - update the DOCKER_HUB_USERNAME in file k8s-manifests/scripts/build_image.sh
    - chmod +x build_image.sh
    - ./build_image.sh

9. Install Helm Packages: Install necessary Helm packages such as Kafka, Prometheus, Grafana, and Nginx Ingress.
    - cd k8s-manifests/scripts
    - chmod +x helm.sh
    - ./helm.sh

10. Apply Manifests: Apply the Kubernetes manifests to deploy services to the cluster.
    - cd k8s-manifests
    - kubectl apply -f manifests    

11. Check Pod and Service Status: Verify the status of pods and services in the cluster.
    - kubectl get pods
    - kubectl get svc

12. Get Load Balancer External IP: Retrieve the external IP of the load balancer.
    - kubectl get svc 
    - Note down External IP of Load Balancer

13. Update /etc/hosts
    - sudo nano /etc/hosts
    - Add the following lines, replacing <External IP> with the load balancer's external IP:
    <External IP>  data-collector.localhost
    <External IP>  data-api.localhost
    <External IP>  data-processor.localhost
    <External IP>  database-writer.localhost
    <External IP>  file-writer.localhost
    <External IP>  grafana.localhost
    <External IP>  prometheus.localhost
    - Save the changes ctrl+O, Enter, ctrl+X

14. Access Services: Services are now exposed and can be accessed via:
    - http://data-collector.localhost
    - http://data-api.localhost
    - http://data-processor.localhost
    - http://database-writer.localhost
    - http://file-writer.localhost
    - http://grafana.localhost
    - http://prometheus.localhost