from django.test import TestCase
from django.shortcuts import reverse
from unittest import TestCase as UnitTestCase
from BinanceTradingApp.trading_client import BinanceAccountClient
from config_file import config, USER_CFG_SECTION


class TestClientAPI(UnitTestCase):
    def test_API_connection(self):
        api_key = config.get(USER_CFG_SECTION, 'api_key')
        api_secret_key = config.get(USER_CFG_SECTION, 'api_secret_key')
        binance_acc = BinanceAccountClient(api_key, api_secret_key)
        all_tickers = binance_acc.get_all_tickers()
        self.assertEqual(all_tickers[0]['symbol'], 'ETHBTC')


class BaseTestClass(TestCase):

    def test_landing_view(self):
        """Test landing view"""
        page_name = "landing_page"
        file_name = "landing.html"

        response = self.client.get(reverse(page_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, file_name)
