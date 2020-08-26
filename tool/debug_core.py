#!/usr/bin/env python3

import requests
import json
import click
import time

API_URL = 'http://localhost:8000/'
route_url = lambda x: API_URL + x

def pretty_date(ts):
    second_diff = time.time() - ts
    day_diff = int(second_diff/86400)
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

def debug_output(request_params: dict, result: str, debug: str):
    '''
    outputs session data on the requested debug level: (silent/)all/error/payload
    '''
    if type(request_params) == dict:
        request_params = json.dumps(request_params)
    error_code = json.loads(result).get('error') if result else None
    if request_params and debug in ['submit', 'all'] or (debug == 'error' and error_code):
        click.echo(request_params)
    if result and debug in ['payload', 'all'] or (debug == 'error' and error_code):
        click.echo(result)


def add_spending_command(amount: int, currency: str, reason: str, date: int, debug: str) -> dict:
    request_params = {
        'amount': amount,
        'currency': currency,
        'reason': reason,
        'date': date
    }
    resp = requests.post(route_url('addspending'), json=request_params)
    data = resp.content.decode()
    debug_output(request_params, data, debug)
    return (json.loads(data))


def update_spending_command(id: int, amount: int, currency: str, reason: str, date: int, debug: str) -> dict:
    request_params = {
        'id': id,
        'amount': amount,
        'currency': currency,
        'reason': reason,
        'date': date
    }
    resp = requests.post(route_url('updatespending'), json=request_params)
    data = resp.content.decode()
    debug_output(request_params, data, debug)
    return (json.loads(data))


def delete_spending_command(id, debug) -> dict:
    request_params = {
        'id': id,
    }
    resp = requests.post(route_url('deletespending'), json=request_params)
    data = resp.content.decode()
    debug_output(request_params, data, debug)
    return (json.loads(data))


def get_spending_command(order_by: str, currency: str, debug) -> dict:
    params = dict()
    if order_by:
        params['order_by'] = order_by
    if currency:
        params['currency'] = currency
    resp = requests.get(route_url('getspending'), params=params)
    data = resp.content.decode()
    debug_output(params, data, debug)
    return (json.loads(data))

class Errors(object):
    '''
    Mirror of server util code
    '''
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