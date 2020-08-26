import django.conf as conf
import re

sqlstate_finder = re.compile('^(R.{4})\n')


def get_currency_id(currency_code):
    return conf.settings.CURRENCY_MAP.get(currency_code.lower())


class Errors(object):
    def __init__(self):
        self.MALFORMED = 1
        self.DATA_ERROR = 2
        self.DB_ERROR = 3
        self.sqlstates = {
            "R0001": "Invalid time.",
            "R0002": "Spending doesn't exist.",
            "R0003": "Invalid currency code.",
        }

    def from_db(self, errmsg):
        match = sqlstate_finder.findall(errmsg)
        return self.sqlstates.get(match[0], 'Unknown error.') if match else 'Unknown error.'