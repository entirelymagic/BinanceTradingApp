from binance.client import Client as BClient


class BinanceAccountClient(BClient):
    """Using Client Binance class perform extended actions."""
    def __init__(self, api_key, api_secret_key):
        super().__init__(api_key, api_secret_key, requests_params=None, tld='com')
        self.api_key = api_key
        self.api_secret_key = api_secret_key

    @staticmethod
    def __first(iterable, condition=lambda x: True):
        try:
            return next(x for x in iterable if condition(x))
        except StopIteration:
            return None

    @property
    def all_market_tickers(self):
        """
        Get ticker price of all coins available
        :return a list of dictionaries as in example bellow:
            [{'symbol': 'ETHBTC', 'price': '0.03422500'}, {...}, ...]
        """
        return self.get_all_tickers()

    def get_market_ticker_price(self, ticker_symbol: str = 'IOTAUSDT') -> None or float:
        """
        Get ticker price of a specific coin
        @:param ticker_symbol - default symbol IOTAUSDT
        @:type str
        """
        for ticker in self.get_symbol_ticker():
            if ticker[u'symbol'] == ticker_symbol:
                return float(ticker[u'price'])
        return None

    def get_market_ticker_price_from_list(self, all_tickers, ticker_symbol) -> float:
        """
        Get ticker price of a specific coin
        """
        ticker = self.__first(all_tickers, condition=lambda x: x[u'symbol'] == ticker_symbol)
        return float(ticker[u'price']) if ticker else None

    def get_currency_balance(self, currency_symbol):
        """
        Get balance of a specific coin
        """
        for currency_balance in self.get_account()[u'balances']:
            if currency_balance[u'asset'] == currency_symbol:
                return float(currency_balance[u'free'])
        return None
