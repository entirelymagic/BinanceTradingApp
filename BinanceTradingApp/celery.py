import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BinanceTradingApp.settings')


# takes as argument the directory that includes the celery.py file
app = Celery('BinanceTradingApp')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'get_values_from_ws': {
        'task': 'binance_trading_bot.tasks.run_sockets',
        'schedule': 30
    }
}

app.autodiscover_tasks()






