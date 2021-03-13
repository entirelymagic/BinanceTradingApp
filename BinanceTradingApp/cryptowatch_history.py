import requests


class CandleHistoryFromCryptowatch:
    """A class to get most recent history of candles for a specific pair of symbols

    @:param pair:str - Required

    @:param period:int - optional

    Period values = {
        60: 1m
        180: 3m
        300: 5m
        900: 15m
        1800: 30m
        3600: 1h
        7200: 2h
        14400: 4h
        21600: 6h
        43200: 12h
        86400: 1d
        259200: 3d
        604800: 1w
    }
    """

    def __init__(self, pair, period=900):
        super().__init__()
        self.pair = pair
        self.period = period
        self.candle_data_list = []
        self.closed = []
        __url = f"https://api.cryptowat.ch/markets/binance/{pair}/ohlc?periods={period}"

        self.data = requests.get(__url).json()

        self._get_list_closed_values()

    def get_last_candle_history(self):
        """
            Return  a list with list of values for the candle
            Candle values in order = [
                                      CloseTime,
                                      OpenPrice,
                                      HighPrice,
                                      LowPrice,
                                      ClosePrice,
                                      Volume,
                                      QuoteVolume
            ]
        """
        return self.data['result'][str(self.period)]

    def _get_list_closed_values(self):
        """Get all candle_data_list data and add it to candle_data_list"""
        k = {
            'CloseTime': None,
            'OpenPrice': None,
            'HighPrice': None,
            'LowPrice': None,
            'ClosePrice': None,
            'Volume': None,
            'QuoteVolume': None
        }

        for candle in self.data['result'][str(self.period)]:

            for key, value in zip(k.keys(), candle):
                k[key] = value
                self.candle_data_list.append(k)
                if key == 'ClosePrice':
                    self.closed.append(value)




