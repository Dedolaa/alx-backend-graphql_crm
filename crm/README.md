# CRM Celery Report Setup

This project uses **Celery + Celery Beat** to generate a weekly CRM report.

## Setup

### 1. Install Redis
Make sure Redis is installed and running:
```bash
redis-server

pip install -r requirements.txt
python manage.py migrate
celery -A crm worker -l info
celery -A crm beat -l info
/tmp/crm_report_log.txt
