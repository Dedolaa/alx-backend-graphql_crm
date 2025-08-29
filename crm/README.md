# Celery Setup for CRM Reports

This guide provides complete instructions for setting up Celery with Django Celery Beat to generate weekly CRM reports.

## Prerequisites

- Python 3.8+
- Redis server
- Django project with GraphQL endpoint
- Existing CRM application with models (Customer, Order, Product)

## Complete Installation Steps

### 1. Install Python Dependencies

```bash
# Add to requirements.txt first
echo "celery==5.3.6" >> requirements.txt
echo "redis==5.0.1" >> requirements.txt
echo "django-celery-beat==2.5.0" >> requirements.txt

# Install all dependencies
pip install -r requirements.txt

Install Redis
Celery requires a message broker. We use **Redis**.

- **Linux / WSL (Ubuntu):**
  ```bash
  sudo apt update && sudo apt install redis-server -y
  sudo systemctl enable redis-server
  sudo systemctl start redis-server

# Apply database migrations
python manage.py migrate

# Celery Worker
celery -A crm worker -l info

# Celery Beat (scheduler)
celery -A crm beat -l info