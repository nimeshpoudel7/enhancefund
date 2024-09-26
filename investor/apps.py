from django.apps import AppConfig

class InvestorConfig(AppConfig):
    name = 'investor'

    def ready(self):
        import investor.signals
