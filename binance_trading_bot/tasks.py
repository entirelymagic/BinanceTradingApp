from BinanceTradingApp.data_manipulation import ws

from celery import shared_task


run_sockets = shared_task(ws.keep_running)


run_sockets()