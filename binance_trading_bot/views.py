from django.shortcuts import render
from django.views import generic
from django.shortcuts import reverse

from .forms import CustomUserCreationForm


class LandingPageView(generic.TemplateView):
    """A generic landing page for landing.html"""
    template_name = 'landing.html'


class SingnupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('login')