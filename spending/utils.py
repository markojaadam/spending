import django.conf as conf
import re
import json

sqlstate_finder = re.compile('^(R.{4})\n')


def get_currency_id(currency_code: str) -> int:
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

    def from_db(self, errmsg: str) -> str:
        match = sqlstate_finder.findall(errmsg)
        return self.sqlstates.get(match[0], 'Unknown error.') if match else 'Unknown error.'

class AppConfig(object):
    def __init__(self, config_file):
        config =  json.loads(open(config_file).read())
        self.server = config.get('server')
        self.db = config.get('db')