# CRM Project Setup

## Install Redis and dependencies
- Install Redis server (https://redis.io/download)
- Install Python dependencies:
  ```bash
  pip install celery django-celery-beat redis django-crontab gql
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

## Run cron jobs
```bash
python manage.py crontab add
```

## Verify logs
- Check `/tmp/crmreportlog.txt` for weekly reports.
- Check `/tmp/crm_heartbeat_log.txt` for heartbeat logs.
- Check `/tmp/low_stock_updates_log.txt` for stock updates.
- Check `/tmp/customer_cleanup_log.txt` for customer cleanup.
- Check `/tmp/order_reminders_log.txt` for order reminders.
