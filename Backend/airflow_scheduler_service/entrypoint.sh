#!/bin/bash
set -e

# Debug environment variable
echo "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: $AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"

# Wait for PostgreSQL connectivity with max attempts
echo "Waiting for PostgreSQL connectivity"
max_attempts=12
attempt=1
while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt of $max_attempts"
    # Use timeout to prevent hangs and capture detailed errors
    timeout 10 psql "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" -c "SELECT 1;" > /tmp/psql.log 2>&1
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "PostgreSQL is ready"
        cat /tmp/psql.log
        break
    else
        echo "PostgreSQL connection failed with exit code $exit_code"
        cat /tmp/psql.log
        if [ $attempt -eq $max_attempts ]; then
            echo "Max attempts reached. Exiting."
            exit $exit_code
        fi
        echo "Retrying in 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    fi
done

# Initialize Airflow database
echo "Running airflow db init"
airflow db init || {
    echo "airflow db init failed"
    exit 1
}

# Create admin user
echo "Creating Airflow admin user"
airflow users create \
    --username airflow \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email hussainathar96@gmail.com \
    --password airflow || true

# Start Airflow webserver and scheduler
echo "Starting Airflow webserver and scheduler"
airflow webserver & airflow scheduler