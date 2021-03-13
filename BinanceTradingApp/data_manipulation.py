import datetime

from time import time


def performance_check(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        value = func(*args, **kwargs)
        t2 = time()
        print(f'Function "{func.__name__}" took {t2 - t1} seconds to execute.')
        return value
    return wrapper


def get_iota_value(acc):
    for item in acc.get_all_tickers():
        if item['symbol'] == 'IOTAUSDT':
            balance = float(acc.get_currency_balance('IOTA'))
            balance_in_USDT = (float(balance) * float(item['price']))
            return "{:.2f}".format(balance_in_USDT)


def to_date(timestamp):
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')




