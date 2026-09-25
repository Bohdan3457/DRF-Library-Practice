# DRF Library Practice

API service for a library management system built with Django REST Framework, PostgreSQL, and Docker.

## Project Features

- User management and authentication (JWT)
- Book management (catalog, inventory)
- Borrowings system (tracking book checkouts and returns)
- Payments integration
- Background tasks processing with Django-Q

## Prerequisites

Make sure you have the following installed on your machine:
- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
   ```bash
   git clone 
   https://github.com/Bohdan3457/DRF-Library-Practice

2. Create a .env file in the root directory based on .env.sample and fill in your configuration variables:
    ```bash
    cp .env.sample .env

3. Build and start the Docker containers in the background:
    ```bash
   docker-compose up --build -d

4. Run database migrations:
   ```bash
   docker-compose exec web python manage.py migrate

5. Create a test superuser automatically:
   ```bash
   docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@library.com').exists() or User.objects.create_superuser('admin@library.com', 'admin12345')"