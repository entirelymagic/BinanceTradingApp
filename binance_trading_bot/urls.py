from django.urls import path
from .views import LandingPageView
# required to provide an app name in order to be included in django main urls
app_name = "binance_trading_bot"

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing-page'),
]
