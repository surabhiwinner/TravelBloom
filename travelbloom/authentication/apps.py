from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    # def ready(self):

    #     try:
    #         import authentication.signals
    #     except ImportError:
    #         pass