from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        autodiscover_modules('stark')