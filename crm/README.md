

# CRM Project Setup

1. Install Redis server (https://redis.io/download)
2. Install Python dependencies:
  ```bash
  pip install celery django-celery-beat redis django-crontab gql
  ```
3. Run migrations:
  ```bash
  python manage.py migrate
  ```
4. Start Celery worker:
  ```bash
  celery -A crm worker -l info
  ```
5. Start Celery Beat:
  ```bash
  celery -A crm beat -l info
  ```
6. Run cron jobs:
  ```bash
  python manage.py crontab add
  ```
7. Verify logs:
  - Check `/tmp/crm_report_log.txt` for weekly reports.
  - Check `/tmp/crm_heartbeat_log.txt` for heartbeat logs.
  - Check `/tmp/low_stock_updates_log.txt` for stock updates.
  - Check `/tmp/customer_cleanup_log.txt` for customer cleanup.
  - Check `/tmp/order_reminders_log.txt` for order reminders.
