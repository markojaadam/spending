from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db import connection
from .utils import get_currency_id, Errors
from .json_schema import ADD_SPENDING_SCHEMA, DELETE_SPENDING_SCHEMA, UPDATE_SPENDING_SCHEMA
from .validators import JSONSchemaValidator
import json
import time

add_validator = JSONSchemaValidator(ADD_SPENDING_SCHEMA)
update_validator = JSONSchemaValidator(UPDATE_SPENDING_SCHEMA)
delete_validator = JSONSchemaValidator(DELETE_SPENDING_SCHEMA)
error = Errors()


def index(request):
    return HttpResponse(str(get_currency_id('USD')))


def addspending(request):
    '''
    Add a spending, submit data JSON template:
    {"amount": 100, "currency": "USD", "reason": "shopping" // nullable, "date": 1598444361 // UNIX epoch}
    '''
    if request.method == 'POST':
        try:
            jsondata = json.loads(request.body)
            add_validator.validate(jsondata)
            jsondata['currency'] = get_currency_id(jsondata['currency'])
            if not jsondata['currency']:
                return HttpResponse(json.dumps({'error': error.DATA_ERROR, 'msg': 'Invalid currency code!'}))
            elif jsondata['date'] > int(time.time()):
                return HttpResponse(json.dumps(
                    {'error': error.DATA_ERROR, 'msg': 'Invalid timestamp!'}))  # You cannot spend in the future
            params = ['amount', 'currency', 'reason', 'date']
            data = [jsondata.get(param) for param in params]
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('api.fun_add_spending', data)
                    _id = cursor.fetchall()
                except Exception as e:
                    return HttpResponse(json.dumps({'error': error.DB_ERROR, 'msg': error.from_db(
                        str(e))}))  # Shouldn't happen
            return HttpResponse(json.dumps({'ok': 1, 'params': {'id': _id[0][0]}}))
        except ValidationError as e:
            return HttpResponse(json.dumps({'error': error.MALFORMED, 'msg': list(e)[0]}))
        except:
            return HttpResponse(json.dumps({'error': error.MALFORMED, 'msg': 'Malformed message!'}))
    else:
        return HttpResponse(status=404)


def getspending(request):
    if request.GET.get('order_by'):
        order = request.GET.get('order_by')
        order = order if order in ['date', 'currency', 'amount'] else None
    else:
        order = None
    if request.GET.get('currency'):
        currency = get_currency_id(request.GET.get('currency'))
    else:
        currency = None
    with connection.cursor() as cursor:
        if currency is not None:
            if order:
                cursor.callproc('api.fun_get_spending_by_currency', [currency, order])
            else:
                cursor.callproc('api.fun_get_spending_by_currency', [currency])
        elif order is not None:
            cursor.callproc('api.fun_get_all_spendings', [order])
        else:
            cursor.callproc('api.fun_get_all_spendings')
        data = cursor.fetchall()
    if currency:
        data_dict = [
            {'id': sp_id, 'amount': amount, 'reason': reason, 'date': date} for sp_id, amount, reason, date in data
        ]
    else:
        data_dict = [
            {'id': sp_id, 'amount': amount, 'currency': currency, 'reason': reason, 'date': date} for
            sp_id, amount, currency, reason, date in data
        ]
    return HttpResponse(json.dumps({'ok': 1, 'data': data_dict}))


def deletespending(request):
    if request.method == 'POST':
        try:
            jsondata = json.loads(request.body)
            delete_validator.validate(jsondata)
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('api.fun_delete_spending',
                                    list(jsondata.values()))
                except Exception as e:
                    return HttpResponse(json.dumps({'error': error.DB_ERROR, 'msg': error.from_db(
                        str(e))}))  # Happens on invalid ID, let the transaction handle it.
            return HttpResponse(json.dumps({'ok': 1}))
        except ValidationError as e:
            return HttpResponse(json.dumps({'error': error.MALFORMED, 'msg': list(e)[0]}))
        except:
            return HttpResponse(json.dumps({'error': error.MALFORMED, 'msg': 'Malformed message!'}))
    else:
        return HttpResponse(status=404)


def updatespending(request):
    if request.method == 'POST':
        try:
            jsondata = json.loads(request.body)
            update_validator.validate(jsondata)
            jsondata['currency'] = get_currency_id(jsondata['currency'])
            if not jsondata['currency']:
                return HttpResponse(json.dumps({'error': error.DATA_ERROR, 'msg': 'Invalid currency code!'}))
            elif jsondata['date'] > int(time.time()):
                return HttpResponse(json.dumps(
                    {'error': error.DATA_ERROR, 'msg': 'Invalid timestamp!'}))  # You cannot spend in the future
            params = ['id', 'amount', 'currency', 'reason', 'date']
            data = [jsondata.get(param) for param in params]
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('api.fun_update_spending',
                                    data)  # The order should be fine thanks to the schema validation
                except Exception as e:
                    return HttpResponse(json.dumps({'error': error.DB_ERROR, 'msg': error.from_db(
                        str(e))}))  # Happens on invalid ID, let the transaction handle it.
            return HttpResponse(json.dumps({'ok': 1}))
        except ValidationError as e:
            return HttpResponse(json.dumps({'error': error.MALFORMED, 'msg': list(e)[0]}))
        except:
            return HttpResponse(json.dumps({'error': error.MALFORMED, 'msg': 'Malformed message!'}))
    else:
        return HttpResponse(status=404)
