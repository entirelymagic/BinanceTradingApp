import time
import threading
import ctypes
from playsound import playsound
from get_stochasticRSI import ThreadedCryptoStats


class CalculateCryptoScore:

    def __init__(self, threaded_crypto: "StochasticRSIThreaded"):
        self.ct = threaded_crypto


def start_monitor_threads(binance_account, ThreadedCryptoStats, symbols: str = 'IOTAUSDT'):
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

    def return_score(self):
        """Every 10 seconds check if :
            - STOCHASTIC RSI is showing sell or buy.
            - MACD is showing sell or buy

        If both show sell or buy, then it a buy or sell signal should be available.
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
                            playsound('changing_sound.mp3')
                        elif not self.buy_trade:
                            playsound('changing_sound.mp3')
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
                            playsound('changing_sound.mp3')
                            self.buy_trade = False
                            self.sell_trade = True
                        elif not self.sell_trade:
                            playsound('changing_sound.mp3')
                            self.buy_trade = False
                            self.sell_trade = True
                            self.profits += float(
                                self.newest_candle_close) - self.value_on_open_trade - self.fee_for_trade
                            self.value_on_open_trade = float(self.newest_candle_close)

                else:
                    #  Stop trade if direction is changing.
                    if (self.open_trade == 1 and self.sell_trade == 1 and float(self.macdhist) > 0
                            or self.open_trade == 1 and self.buy_trade == 1 and float(self.macdhist) < 0):
                        self.open_trade = 0

                # check if oversold or overbought

            except TypeError:
                pass
            try:
                if self.buy_signal and float(self.macdhist) < -0.005:
                    self.strong_buy = True
                    self.strong_sell = False
                    playsound("mixkit-epic-orchestra-transition-2290.wav")
                elif self.sell_signal and float(self.macdhist) > 0.005:
                    self.strong_sell = True
                    self.strong_buy = False
                    playsound("mixkit-epic-orchestra-transition-2290.wav")
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
                    print(
                        f"""
                        ********************************************************************
                        
                            Crypto Checked =  {self.symbol} On {self.KLINE_INTERVAL} interval.
                            Profits = {self.profits}
                            Current_price = {self.newest_candle_close}
                            value_on_open_trade = {self.value_on_open_trade}
                            potential_profit_so_far = {self.potential_profit_so_far}

                            Strong trade = {"Strong Sell" if self.strong_sell else "Strong Buy" if self.strong_buy else None}
                            self.buy_signal = {self.buy_signal}
                            self.sell_signal = {self.sell_signal}
                            self.open_trade = {self.open_trade}

                            self.rsi_bullish = {self.rsi_bullish}
                            self.stc_bullish = {self.stc_bullish}
                            bb_percent = {self.newest_bb_percent}

                            macd {self.macd}
                            macdsignal: {self.macdsignal}
                            macdhist: {self.macdhist}

                            newest_candle_K {self.newest_candle_K}
                            newest_candle_D {self.newest_candle_D}
                            direction {self.moving_direction}
                            
                            MESA Adaptive Moving Average = {
                        "Bullish" if float(self.mama) - float(self.fama) > 0 else "Bearish"
                        }

                            """)

            except TypeError:
                pass

            time.sleep(5)
