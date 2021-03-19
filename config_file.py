import configparser
import os
import time
import sys
import logging
import datetime

from pprint import pprint
from playsound import playsound

from BinanceTradingApp.trading_client import BinanceAccountClient
from get_stochasticRSI import ThreadedCryptoStats
from decizion_maker import CalculateCryptoScore, start_monitor_threads, CryptoMonitorThread

# Config consts
CFG_FL_NAME = 'data/user.cfg'
USER_CFG_SECTION = 'binance_user_config'

# Init config
config = configparser.ConfigParser()
if not os.path.exists(CFG_FL_NAME):
    print('No configuration file (user.cfg) found! See README.')
    exit()
config.read(CFG_FL_NAME)

# get django secret key from user.cfg
DJANGO_SECRET_KEY = config.get(USER_CFG_SECTION, 'django_secret_key')

# Get supported coin list from supported_coin_list file
with open('data/supported_coin_list') as f:
    supported_coin_list = f.read().upper().splitlines()

# Telegram bot
TELEGRAM_CHAT_ID = config.get(USER_CFG_SECTION, 'botChatID')
TELEGRAM_TOKEN = config.get(USER_CFG_SECTION, 'botToken')
BRIDGE = config.get(USER_CFG_SECTION, 'bridge')

# Logger setup
logger = logging.getLogger('crypto_trader_logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('crypto_trading.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


def set_acc() -> 'BinanceAccountClient':
    """Using the API key and secret key configure the a binance account object."""
    api_key = config.get(USER_CFG_SECTION, 'api_key')
    api_secret_key = config.get(USER_CFG_SECTION, 'api_secret_key')
    account = BinanceAccountClient(api_key, api_secret_key)
    return account


crypto_winnings = {
    '12h': {
        'winnings': 0,
        'ALERT_CHANGE': '',
        'change_on_price': '',
        'positions': 0,
    },
    '1h': {
        'winnings': 0,
        'ALERT_CHANGE': '',
        'change_on_price': 0,
        'positions': 0,
    },
    '15m': {
        'winnings': 0,
        'ALERT_CHANGE': '',
        'change_on_price': 0,
        'positions': 0,
    },
    '5m': {
        'winnings': 0,
        'ALERT_CHANGE': '',
        'change_on_price': 0,
        'positions': 0,
    },
}

binance_account = set_acc()

tickers = binance_account.get_all_tickers()

# start_monitor_threads(binance_account, ThreadedCryptoStats, "IOTAUSDT")


coins = ['OMG', 'FTM', 'NEAR', 'XLM', 'COTI', 'IOTA', 'RVN', 'HOT', 'CHZ', 'BTC', 'DEGO', 'VET', 'ADA', 'BNB', 'ONE']


def run_multiple_checks(crypto_coin_list: list):
    intervals_to_check = ['1m', '15m', '1h']
    for item in crypto_coin_list:
        for i in intervals_to_check:
            detail = CryptoMonitorThread(binance_account, symbol=item + 'USDT', KLINE_INTERVAL=i)
            detail.return_score()
            detail.return_score()
            del detail


def run_single_values(
        single_coin_check: str,
        profits: float,
        value_on_open_trade: float,
        buy_signal: bool = None,
        sell_signal: bool = None,
        KLINE_INTERVAL: str = '1m'
) -> None:
    # shot statistics on start for 1 hour then Close
    single_coin = CryptoMonitorThread(binance_account, symbol=single_coin_check + 'USDT', KLINE_INTERVAL='1h')
    # set this on if trade opened already
    single_coin.profits = profits
    single_coin.buy_trade = buy_signal
    single_coin.sell_trade = sell_signal
    single_coin.value_on_open_trade = value_on_open_trade

    single_coin.return_score()
    single_coin.return_score()
    del single_coin

    # shot statistics on start for 1m in a loop
    single_coin = CryptoMonitorThread(binance_account, symbol=single_coin_check + 'USDT', KLINE_INTERVAL=KLINE_INTERVAL)

    # set this on if trade opened already
    single_coin.profits = profits
    single_coin.buy_signal = buy_signal
    single_coin.sell_signal = sell_signal
    single_coin.value_on_open_trade = value_on_open_trade
    # Check continuously
    while True:
        single_coin.return_score()


# run_single_values(
#     single_coin_check='XLM',
#     buy_signal=None,
#     sell_signal=None,
#     value_on_open_trade=0,
#     profits=0,
#     KLINE_INTERVAL='1m')

while True:
    run_multiple_checks(coins)

