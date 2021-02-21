import configparser
import os
import logging.handlers


# Config consts
CFG_FL_NAME = 'data/user.cfg'
USER_CFG_SECTION = 'binance_user_config'


# Init config
config = configparser.ConfigParser()
if not os.path.exists(CFG_FL_NAME):
    print('No configuration file (user.cfg) found! See README.')
    exit()
config.read(CFG_FL_NAME)

# Logger setup
logger = logging.getLogger('crypto_trader_logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('data/crypto_trading.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# logging to console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# get django secret key from user.cfg
DJANGO_SECRET_KEY = config.get(USER_CFG_SECTION, 'django_secret_key')

# Get supported coin list from supported_coin_list file
with open('data/supported_coin_list') as f:
    supported_coin_list = f.read().upper().splitlines()

