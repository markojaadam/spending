import django.conf as conf
import re
import json
import time

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
        config = json.loads(open(config_file).read())
        self.server = config.get('server')
        self.db = config.get('db')


def pretty_date(ts: int) -> str:
    second_diff = time.time() - ts
    day_diff = int(second_diff / 86400)
    if day_diff < 0 or not ts:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(int(second_diff)) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


def format_amount(amount: float) -> str:
    if int(amount) == amount:
        return ("%.0f" % amount)
    elif int(amount * 10) == amount * 10:
        return ("%.1f" % amount)
    else:
        return ("%.2f" % amount)
