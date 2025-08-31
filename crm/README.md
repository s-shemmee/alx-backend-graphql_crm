
# Weekly CRM Report via Celery

This optional task uses Celery and django-celery-beat to generate a weekly CRM report summarizing:
- Total number of customers
- Total number of orders
- Total revenue from orders

The report runs **every Monday at 6:00 AM** and logs to `/tmp/crm_report_log.txt`.

---

## 🛠️ Setup Instructions

### 1. Install Redis and Python Dependencies

Install Redis:
```bash
sudo apt update
sudo apt install redis
```

Install required Python packages:
```bash
pip install -r requirements.txt
```

Make sure `requirements.txt` includes:
```
celery==5.3.6
django-celery-beat==2.6.0
django-crontab
gql
```

---

### 2. Configure Django

- Add `'django_celery_beat'` and `'django_crontab'` to `INSTALLED_APPS` in `crm/settings.py`
- Add the following Celery configuration in `crm/settings.py`:
```python
from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

- Add the following CRONJOBS configuration in `crm/settings.py`:
```python
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
```

---

### 3. Run Migrations

```bash
python manage.py migrate
```

---

### 4. Start Services

Start the Celery worker:
```bash
celery -A crm worker -l info
```

Start Celery Beat scheduler:
```bash
celery -A crm beat -l info
```

---

### 5. Setup and Run Cron Jobs

Add cron jobs:
```bash
python manage.py crontab add
```

---

### 6. Verify Output

Check the file `/tmp/crm_report_log.txt` after Monday 6 AM or trigger the task manually:
```bash
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()
```

Expected log format:
```
2025-09-01 06:00:00 - Report: 10 customers, 24 orders, 1024.50 revenue
```

Check other log files for cron jobs:
- `/tmp/crm_heartbeat_log.txt` for heartbeat logs
- `/tmp/low_stock_updates_log.txt` for stock updates
- `/tmp/customer_cleanup_log.txt` for customer cleanup
- `/tmp/order_reminders_log.txt` for order reminders

