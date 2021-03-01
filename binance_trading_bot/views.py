from django.shortcuts import render
from django.views import generic
from django.shortcuts import reverse
from config_file import acc
from data_manipulation import get_iota_value, ws
from .forms import CustomUserCreationForm


class LandingPageView(generic.ListView):
    """A generic landing page for landing.html"""
    template_name = 'landing.html'
    context_object_name = 'landing'

    def get_queryset(self, *args, **kwargs):
        queryset = {
            'iota_value_in_USDT': get_iota_value(acc),
            'IOTAUSDT_last_price': acc.get_ticker(symbol='IOTAUSDT')['lastPrice'],
            'IOTAUSDT_details': acc.get_ticker(symbol='IOTAUSDT'),
            'IOTAUSDT_history_trades': acc.get_currency_balance(currency_symbol="USDT"),
            'websocket': ws.run_forever(),
        }
        return queryset


class SingnupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('login')



