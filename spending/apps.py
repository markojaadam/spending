from django.apps import AppConfig
import django.conf as conf


class spendingConfig(AppConfig):
    def __init__(self, app_name, app_module):
        super(spendingConfig, self).__init__(app_name, app_module)
        self.currency_data = dict()

    name = 'spending'
    verbose_name = 'Django backend to track my spendings.'

    def ready(self):
        from models import Currency
        allobj = Currency.objects.all()
        conf.settings.CURRENCY_MAP = dict([(each.code.lower(), int(each.pkey_id)) for each in
                                           allobj])  # map id-code pairs only once when server initialized
