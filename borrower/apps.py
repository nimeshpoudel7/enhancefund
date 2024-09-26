from django.apps import AppConfig


class BorrowerConfig(AppConfig):
    name = 'borrower'

    def ready(self):
        import borrower.signals
