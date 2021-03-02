import asyncio
from django.shortcuts import render
from django.views import generic
from django.shortcuts import reverse
from config_file import acc
from data_manipulation import get_iota_value, SOCKET
from .forms import CustomUserCreationForm
from cryptowatch_history import CandleHistoryFromCryptowatch


class LandingPageView(generic.ListView):
    """A generic landing page for landing.html"""
    template_name = 'landing.html'
    context_object_name = 'landing'

    def get_queryset(self, *args, **kwargs):
        """Get the queryset/context for LandingPageView"""
        queryset = {
            'iota_value_in_USDT': get_iota_value(acc),
            'IOTAUSDT_last_price': acc.get_ticker(symbol='IOTAUSDT')['lastPrice'],
            'IOTAUSDT_details': acc.get_ticker(symbol='IOTAUSDT'),
            'USDT_balance': acc.get_currency_balance(currency_symbol="USDT"),
            'crypto_history': CandleHistoryFromCryptowatch('IOTAUSDT', 900).closed,
            'socket_url': SOCKET,
        }
        return queryset


class SingnupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('login')



