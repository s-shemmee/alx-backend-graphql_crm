# CRM Celery Setup

## Install Redis and dependencies
- Install Redis server (https://redis.io/download)
- Install Python dependencies:
  ```bash
  pip install celery django-celery-beat redis
  ```

## Run migrations
```bash
python manage.py migrate
```

## Start Celery worker
```bash
celery -A crm worker -l info
```

## Start Celery Beat
```bash
celery -A crm beat -l info
```

## Verify logs
Check `/tmp/crm_report_log.txt` for weekly reports.
