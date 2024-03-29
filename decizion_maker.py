import time
import logging
from datetime import datetime
from static.sounds.alert_sounds import play_buy_or_sell_sound, play_strong_signals

from get_stochasticRSI import ThreadedCryptoStats

buy_or_sell_sound = "static/sound/changing_sound.mp3"


# Logger setup
def setup_logger(logger_name, log_file, level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    formatter =logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a+')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


setup_logger('long_log', 'long_log'+".txt", level=logging.DEBUG)
setup_logger('short_log', 'short_log'+".txt", level=logging.DEBUG)
long_log = logging.getLogger('long_log')
short_log = logging.getLogger('short_log')


class CalculateCryptoScore:

    def __init__(self, threaded_crypto: "StochasticRSIThreaded"):
        self.ct = threaded_crypto


def start_monitor_threads(binance_account, symbols: str = 'IOTAUSDT'):
    """Start threads for symbols. on a specific account"""

    crypto_12h = ThreadedCryptoStats(binance_account, symbol=symbols, KLINE_INTERVAL='12h')
    crypto_12h.daemon = True
    crypto_12h.start()

    crypto_1h = ThreadedCryptoStats(binance_account, symbol=symbols, KLINE_INTERVAL='1h')
    crypto_1h.daemon = True
    crypto_1h.start()

    crypto_15m = ThreadedCryptoStats(binance_account, symbol=symbols, KLINE_INTERVAL='15m')
    crypto_15m.daemon = True
    crypto_15m.start()

    crypto_5m = ThreadedCryptoStats(binance_account, symbol=symbols, KLINE_INTERVAL='5m')
    crypto_5m.daemon = True
    crypto_5m.start()

    crypto_1m = ThreadedCryptoStats(binance_account, symbol=symbols, KLINE_INTERVAL='1m')
    crypto_1m.daemon = True
    crypto_1m.start()

    return crypto_12h, crypto_1h, crypto_15m, crypto_5m


class CryptoMonitorThread(ThreadedCryptoStats):
    """Open a thread and return scores."""

    def __init__(self, binance_account, symbol: str = 'IOTAUSDT', KLINE_INTERVAL: str = '1m'):
        super().__init__(binance_account, symbol, KLINE_INTERVAL)
        self.daemon = True
        self.start()
        self.bullish = None
        self.rsi_bullish = None
        self.stc_bullish = None
        self.timing = None
        self.buy_signal = None
        self.sell_signal = None
        self.open_trade = 0
        self.buy_trade = None
        self.sell_trade = None
        self.strong_sell = None
        self.strong_buy = None
        self.profits = 0
        self.value_on_open_trade = 0
        self.fee_for_trade = 0
        self.potential_profit_so_far = 0
        self.sleep_time = 5

        self.strong_signals = []

    def return_score(self):
        """Develop a decision to sell or buy made on available information.
        """
        if True:
            try:
                if float(self.macdhist) > 0:
                    self.stc_bullish = True
                else:
                    self.stc_bullish = False
                self.fee_for_trade = float(self.newest_candle_close) * 0.002
            except TypeError:
                pass
            try:
                if float(self.moving_direction) > 0:
                    self.rsi_bullish = True
                else:
                    self.rsi_bullish = False
            except TypeError:
                pass

            try:
                # Check if buy Opportunity is available
                if (float(self.newest_candle_K) + float(self.newest_candle_D)) / 2 < 30:
                    if self.rsi_bullish and self.stc_bullish:
                        self.buy_signal = True
                        self.sell_signal = False
                        self.open_trade = 1

                        if self.value_on_open_trade == 0:
                            self.value_on_open_trade = float(self.newest_candle_close)
                            self.buy_trade = True
                            self.sell_trade = False
                            # play_buy_or_sell_sound()
                        elif not self.buy_trade:
                            # play_buy_or_sell_sound()
                            self.buy_trade = True
                            self.sell_trade = False
                            self.profits += self.value_on_open_trade - float(
                                self.newest_candle_close) - self.fee_for_trade
                            self.value_on_open_trade = float(self.newest_candle_close)

                # Check if sell Opportunity is available
                elif (float(self.newest_candle_K) + float(self.newest_candle_D)) / 2 > 70:
                    if not self.rsi_bullish and not self.stc_bullish:
                        self.buy_signal = False
                        self.sell_signal = True
                        self.open_trade = 1
                        # playsound()
                        if self.value_on_open_trade == 0:
                            self.value_on_open_trade = float(self.newest_candle_close)
                            # play_buy_or_sell_sound()
                            self.buy_trade = False
                            self.sell_trade = True
                        elif not self.sell_trade:
                            # play_buy_or_sell_sound()
                            self.buy_trade = False
                            self.sell_trade = True

                            self.profits += float(
                                self.newest_candle_close) - self.value_on_open_trade - self.fee_for_trade
                            self.value_on_open_trade = float(self.newest_candle_close)

                else:
                    #  Stop trade if direction is changing.
                    if (self.open_trade == 1 and self.sell_trade and float(self.macdhist) > 0
                            or self.open_trade == 1 and self.buy_trade and float(self.macdhist) < 0):
                        self.open_trade = 0

                # check if oversold or overbought

            except TypeError:
                pass
            try:
                if self.buy_signal and float(self.macdsignal) < -self.macd_percents:

                    self.strong_buy = True
                    self.strong_sell = False
                    play_strong_signals()
                elif self.sell_signal and float(self.macdsignal) > self.macd_percents:
                    self.strong_sell = True
                    self.strong_buy = False
                    play_strong_signals()
                else:
                    self.strong_sell = None
                    self.strong_buy = None
            except TypeError:
                pass
            try:

                if self.macdhist:
                    self.potential_profit_so_far = (
                            (float(self.newest_candle_close) - self.value_on_open_trade if self.buy_signal else
                             self.value_on_open_trade - float(self.newest_candle_close) if self.sell_signal else 0)
                            - self.fee_for_trade)

                    long_log.info(
                        f"""
                        Current Time: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                        ********************************************************************
                            {'*'*68 if self.buy_signal or self.buy_signal else ''}
                            Crypto Checked =  {self.symbol}, interval: {self.KLINE_INTERVAL} .
                            Profits = {self.profits}
                            Current_price = {self.newest_candle_close}
                            Last Candle Close Price = {self.last_candle_close}
                            value_on_open_trade = {self.value_on_open_trade}
                            Potential profits = {self.potential_profit_so_far}
                            
                            ---------------------------------------------------------------------
                            Trade Signal = {
                                            "Strong Sell " if self.strong_sell else 
                                            "Strong Buy" if self.strong_buy else 
                                            'BUY SIGNAL' if self.buy_signal else 
                                            'SELL SIGNAL' if self.sell_signal else
                                            '---'
                            }
                            ---------------------------------------------------------------------
                            
                            self.open_trade = {self.open_trade}

                            self.rsi_bullish = {self.rsi_bullish}
                            self.stc_bullish = {self.stc_bullish}
                            bb_percent = {float(self.newest_bb_percent)}

                            macd {self.macd}
                            macdsignal: {self.macdsignal}
                            macdhist: {self.macdhist}
                            percent_macd {self.macd_percents}

                            newest_candle_K {self.newest_candle_K}
                            newest_candle_D {self.newest_candle_D}
                            direction {self.moving_direction}
                            
                            MESA Adaptive Moving Average = {
                        "Bullish" if float(self.mama) - float(self.fama) > 0 else "Bearish"
                        }
                            {self.mama} { self.fama}

                            """)
                    if self.strong_sell or self.strong_buy:
                        short_log.info(
                            f"""
                            Current Time: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                            Crypto Checked =  {self.symbol}, interval: {self.KLINE_INTERVAL} .
                            Price = {self.newest_candle_close}
                            ---------------------------------------------------------------------
                            Trade Signal = {
                                            "Strong Sell " if self.strong_sell else 
                                            "Strong Buy" if self.strong_buy else 
                                            'BUY SIGNAL' if self.buy_signal else 
                                            'SELL SIGNAL' if self.sell_signal else
                                            '---'
                            }
                            ---------------------------------------------------------------------
                            """)

            except TypeError:
                pass

            time.sleep(self.sleep_time)

