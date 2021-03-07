import websocket
import json
from BinanceTradingApp.cryptowatch_history import CandleHistoryFromCryptowatch

from asgiref.sync import sync_to_async

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

last_message_from_socket = []


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
    last_message_from_socket.append(close)
    if is_candle_closed:
        closes.append(float(close))
        print('Last from closes: ' + str(closes[-1]))


# Create websocket app to take actions
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
get_closes = sync_to_async(ws.run_forever, thread_sensitive=True)
