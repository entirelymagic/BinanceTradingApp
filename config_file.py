import configparser
import os
import json
import pprint
from time import sleep
from BinanceTradingApp.trading_client import BinanceAccountClient

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


def main():
    api_key = config.get(USER_CFG_SECTION, 'api_key')
    api_secret_key = config.get(USER_CFG_SECTION, 'api_secret_key')
    binance_acc = BinanceAccountClient(api_key, api_secret_key)

    all_tickers = binance_acc.get_all_tickers()

    print(all_tickers)
    for item in all_tickers:
        if item['symbol'] == 'IOTAUSDT':
            balance = float(binance_acc.get_currency_balance('IOTA'))

            print(float(balance) * float(item['price']))
            print(balance*1.2)


if __name__ == "__main__":
    main()
