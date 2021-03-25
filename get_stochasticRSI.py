# coding: utf-8
import pandas as pd
import talib
import numpy as np  # computing multidimensional arrays
import datetime
import time
import threading


class ThreadedCryptoStats(threading.Thread):
    """Take a binance_account client and in onrder to return the latest data regarding RSI of a symbol amd interval
    @:param: client - A binance account client initiated
    @:param: symbol - crypto symbol default IOTAUSDT
    @:param: KLINE_INTERVAL should be the interval selected to calculate the RSI

    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

    """

    def __init__(self, client: "BinanceAccountClient", symbol: str = 'IOTAUSDT', KLINE_INTERVAL: str = '1h'):
        super().__init__()
        self.client = client
        self.symbol = symbol
        self.KLINE_INTERVAL = KLINE_INTERVAL

        self.moving_direction = None
        self.rsi_difference = None

        self.my_stoch_rsi = None
        self.newest_candle_start = None  # gets last time
        self.newest_candle_end = None  # gets current time?
        self.newest_candle_close = None  # gets last close
        self.newest_candle_RSI = None  # gets last rsi
        self.newest_candle_K = None  # gets last rsi
        self.newest_candle_D = None  # gets last rsi
        self.newest_bb_upper_band = None
        self.newest_bb_middle_band = None
        self.newest_bb_lower_band = None
        self.bb_percent = []
        self.newest_bb_percent = None
        self.bbp_direction = None
        self.rsi_direction_minus_rsi_difference = None
        self.newest_high = None
        self.newest_low = None
        self.ADX = None
        self.mama = None
        self.fama = None
        self.starting_MAMA_dif = None
        self.macd = None
        self.macdsignal = None
        self.macdhist = None
        self.macd_percents = None
        self.last_candle_close = None

        self.rsi_K = None
        self.rsi_D = None

    # StochasticRSI Function
    @staticmethod
    def _stochasticRSI(close, high, low, smoothk, smoothd, n):
        lowest_low = pd.Series.rolling(low, window=n, center=False).min()
        highest_high = pd.Series.rolling(high, window=n, center=False).max()
        K = pd.Series.rolling(100 * ((close - lowest_low) / (highest_high - lowest_low)), window=smoothk).mean()
        D = pd.Series.rolling(K, window=smoothd).mean()
        return K, D

    @staticmethod
    def _bollinger_bands_percent(close, high, middle, low):
        pass

    def run(self):
        # Main program
        while True:
            # ping client to avoid timeout

            # Get Binance Data into dataframe
            candles = self.client.get_klines(symbol=self.symbol, interval=self.KLINE_INTERVAL)
            df = pd.DataFrame(candles)
            df.columns = ['timestart', 'open', 'high', 'low', 'close', '?', 'timeend', '?', '?', '?', '?', '?']
            df.timestart = [datetime.datetime.fromtimestamp(i / 1000) for i in df.timestart.values]
            df.timeend = [datetime.datetime.fromtimestamp(i / 1000) for i in df.timeend.values]

            # Compute RSI after fixing data
            float_data = [float(x) for x in df.close.values]
            np_float_data = np.array(float_data)
            rsi = talib.RSI(np_float_data, 120)
            df['rsi'] = rsi

            # Compute StochRSI using RSI values in Stochastic function
            self.my_stoch_rsi = self._stochasticRSI(df.rsi, df.rsi, df.rsi, 3, 3, 320)
            df['MyStochrsiK'], df['MyStochrsiD'] = self.my_stoch_rsi

            #################################### End of Main #############################################
            # WARNING: If Logging is removed uncomment the next line.
            time.sleep(2)  # Sleep for 1 second. So IP is not rate limited.
            # Can be faster. Up to 1200 requests per minute.

            self.newest_candle_start = df.timestart.astype(str).iloc[-1]  # gets last time
            self.newest_candle_end = df.timeend.astype(str).iloc[-1]  # gets current time?
            self.newest_candle_close = df.close.iloc[-1]  # gets last close
            self.newest_candle_RSI = df.rsi.astype(str).iloc[-1]  # gets last rsi
            self.newest_candle_K = df.MyStochrsiK.astype(str).iloc[-1]  # gets last rsi
            self.newest_candle_D = df.MyStochrsiD.astype(str).iloc[-1]  # gets last rsi
            self.newest_high = df.high.astype(str).iloc[-1]
            self.newest_low = df.low.astype(str).iloc[-1]

            self.last_candle_close = df.close.iloc[-2]  # gets second last

            # get moving_Direction
            self.moving_direction = str(
                float(df.MyStochrsiK.astype(str).iloc[-1]) - float(df.MyStochrsiD.astype(str).iloc[-1]))
            self.rsi_difference = str(
                (float(df.MyStochrsiK.astype(str).iloc[-7]) - float(df.MyStochrsiD.astype(str).iloc[-7])) +
                (float(df.MyStochrsiK.astype(str).iloc[-1]) - float(df.MyStochrsiD.astype(str).iloc[-1]))
            )

            # Compute Bollinger bands and percents
            bbands = talib.BBANDS(np_float_data, timeperiod=20)
            self.newest_bb_upper_band = bbands[0][-1]
            self.newest_bb_middle_band = bbands[1][-1]
            self.newest_bb_lower_band = bbands[2][-1]
            self.newest_bb_percent = str(
                        ((float(self.newest_candle_close) - float(self.newest_bb_lower_band)) /
                        (float(self.newest_bb_upper_band) - float(self.newest_bb_lower_band))
                         )*100
            )
            self.bb_percent.append(self.newest_bb_percent)

            self.rsi_direction_minus_rsi_difference = str(float(self.moving_direction) - float(self.rsi_difference))


            try:
                self.bbp_direction = str(float(self.bb_percent[-1]) - (float(self.bb_percent[-20])))

            except IndexError:
                pass

            self.macd_percents = float(self.newest_candle_close) * 0.005
            # aDX
            # self.ADX = talib.ADX(self.newest_high, self.newest_low, self.newest_candle_close)

            # MAMA
            self.MAMA = talib.MAMA(np_float_data)
            df['mama'], df['fama'] = self.MAMA
            self.mama = df.mama.astype(str).iloc[-1]
            self.fama = df.fama.astype(str).iloc[-1]

            if not self.fama and not self.starting_MAMA_dif:
                self.starting_MAMA_dif = self.mama - self.fama

            # MACD

            self.MACD = talib.MACD(np_float_data)
            df['macd'], df['macdsignal'], df['macdhist'] = self.MACD
            self.macd = df.macd.astype(str).iloc[-1]
            self.macdsignal = df.macdsignal.astype(str).iloc[-1]
            self.macdhist = df.macdhist.astype(str).iloc[-1]

            self.new_rsi = talib.STOCHRSI(np_float_data,timeperiod=120)
            df['rsi_K'],  df['rsi_D'] = self.new_rsi
            self.rsi_K = df.rsi_K.astype(str).iloc[-1]
            self.rsi_D = df.rsi_D.astype(str).iloc[-1]

            """1. Moving Average Convergence Divergence (MACD) The Moving Average Convergence Divergence (MACD) is 
            one of the most popular momentum indicators. The MACD uses two indicators – moving averages – turning 
            them into an oscillator by taking the longer average out of the shorter average. It means that the MACD 
            indicates momentum as it oscillates between moving averages as they converge, overlap, and move away from 
            one another. 

            As mentioned above, the MACD makes use of two moving averages. While it is up to the discretion of the 
            trader or analyst, the indicator typically uses the 12-day and 26-day exponential moving averages (EMAs), 
            subtracting the 26-day from the 12-day. The result is the MACD line, which is then usually graphed with a 
            9-day EMA, acting as a signal line that can identify price movement turns. 
            
            The truly important aspect of the MACD is the histogram, which reveals the difference between the MACD 
            line and the 9-day EMA. When the histogram is positive – over the zero-midpoint line but begins to fall 
            towards the midline – it signals a weakening uptrend. On the flipside, when the histogram is negative, 
            under the zero-midpoint line but begins to climb towards it, it signals the downtrend is weakening. 

             
            
            2. Relative Strength Index (RSI) The Relative Strength Index (RSI) is another popular momentum indicator. 
            Also an oscillator, the RSI acts as a metric for price changes and the speed at which they change. The 
            indicator fluctuates back and forth between zero and 100. Signals can be spotted by traders and analysts 
            if they look for divergences, failed swings of the oscillator, and when the indicator crosses over the 
            centerline. 
            
            Any rising RSI values above 50 signal positive, uptrend momentum, though, if the RSI hits 70 or above, 
            it’s often an indication of overbought conditions. Conversely, RSI readings that decrease below 50 show 
            negative, downtrend momentum. If RSI readings are below 30, though, it is an indication of possible 
            oversold conditions. 
            
             
            
            3. Average Directional Index (ADX) Finally, the Average Directional Index (ADX) must be mentioned. In 
            reality, creator Welles Wilder established the Directional Movement System – consisting of the ADX, 
            the Minus Directional Indicator (-DI), and the Plus Directional Indicator (+DI) – as a group that could 
            be used to help measure both the momentum and direction of price movements. 
            
            The ADX is derived from the smoothed averages of the -DI and +DI, which are themselves derived from the 
            comparison of two consecutive lows and their respective highs. The index is the portion of the 
            Directional Movement System that acts as a metric for the strength of a trend, regardless of its 
            direction. It’s important to note that with the ADX, values of 20 or higher suggest the presence of a 
            trend. For any reading lower than 20, the market is viewed as “directionless.” """

    def stop(self):
        self._stop.set()