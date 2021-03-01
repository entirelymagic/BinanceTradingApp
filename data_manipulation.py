import datetime
import talib
import websocket
import json

import datetime as dt

from pprint import pprint
from config_file import acc
from cryptowatch_history import CandleHistoryFromCryptowatch

SOCKET = "wss://stream.binance.com:9443/ws/iotausdt@kline_1m"

RSI_PERIOD = 120
RSI_OVERBOUGHT = 80
RSI_OVERSOLD = 20
TRADE_SYMBOL = 'IOTAUSDT'

# Candlestick intervals that can be used with socket url
Candlestick_chart_intervals = ["1m",
                               "3m",
                               "5m",
                               "15m",
                               "30m",
                               "1h",
                               "2h",
                               "4h",
                               "6h",
                               "8h",
                               "12h",
                               "1d",
                               "3d",
                               "1w",
                               "1M", ]

cripto_history = CandleHistoryFromCryptowatch(TRADE_SYMBOL, 900)

closes = cripto_history.closed


def on_open(ws):
    print("Opened")


def on_close(ws):
    print("Closed")


def on_message(ws, message):
    global closes
    print("Message received")
    json_message = json.loads(message)
    # pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    print(close)
    if is_candle_closed:
        closes.append(float(close))
        print(closes)


# Create websocket app to take actions
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)


def get_iota_value(acc):
    for item in acc.get_all_tickers():
        if item['symbol'] == 'IOTAUSDT':
            balance = float(acc.get_currency_balance('IOTA'))
            balance_in_USDT = (float(balance) * float(item['price']))
            return "{:.2f}".format(balance_in_USDT)


def to_date(timestamp):
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')
