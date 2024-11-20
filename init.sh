#!/bin/bash

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Navigate to the project directory
cd credit_system
echo "Making migrations..."

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Trigger background tasks
echo "Triggering background tasks for data ingestion..."
pwd
python manage.py shell -c "from core.tasks import ingest_data; ingest_data.delay('init_data/customer_data.xlsx','init_data/loan_data.xlsx')"

echo "All tasks started successfully!"
