from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db import connection
from django.template.loader import render_to_string
from .utils import get_currency_id, Errors, pretty_date, format_amount
from .json_schema import ValidationSchema
from .validators import JSONSchemaValidator
import json
import time

error = Errors()
validation_schema = ValidationSchema()


def index(request) -> HttpResponse:
    if request.method == 'GET':
        spend_data = get_spending_list()
        print(type(spend_data))
        index_template = render_to_string('list.html', {'data': spend_data})
        return HttpResponse(index_template)
    else:
        return HttpResponse(status=404)


def addspending(request) -> HttpResponse:
    '''
    POST endpoint
    Add a spending, submit data JSON template:
        {"amount": 100, "currency": "USD", "reason": "shopping" // nullable, "date": 1598444361 // UNIX epoch}
    All fields are mandatory.
    Returns:
        identifier of the submitted spending: {'ok': 1, 'data': {'id':1}}
    '''
    if request.method == 'POST':
        try:
            jsondata = json.loads(request.body)
            add_validator = JSONSchemaValidator(validation_schema.ADD_SPENDING_SCHEMA)
            add_validator.validate(jsondata)
            jsondata['currency'] = get_currency_id(jsondata['currency'])
            if not jsondata['currency']:
                return HttpResponse(json.dumps({'error': error.DATA_ERROR, 'msg': 'Invalid currency code!'}))
            jsondata['amount'] = int(jsondata['amount'] * 100)
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


def get_spending_list():
    with connection.cursor() as cursor:
        cursor.callproc('api.fun_get_all_spendings')
        data = cursor.fetchall()
    data_dict = [
        {'id': sp_id, 'amount': format_amount(float(amount) / 100), 'currency': currency,
         'reason': reason if reason else '', 'date': pretty_date(date)} for
        sp_id, amount, currency, reason, date in data
    ]
    return (data_dict)


def getspending(request) -> HttpResponse:
    '''
    GET endpoint
    Get our spendings. possibe optional query parameters:
        order_by: order by a parameter {date (default)/ currency / amount}
        currency: filter by a currency
        invalid values will be ignored (e.g. currency=XYZ)
        example: API_URL/getspending?order_by=date&currency=USD
    Returns:
        array of spendings in JSON format
    '''
    if request.method == 'GET':
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
                {'id': sp_id, 'amount': float(amount) / 100, 'currency': currency, 'reason': reason, 'date': date} for
                sp_id, amount, currency, reason, date in data
            ]
        return HttpResponse(json.dumps({'ok': 1, 'data': data_dict}))
    else:
        return HttpResponse(status=404)


def deletespending(request) -> HttpResponse:
    '''
    POST endpoint
    Delete a spending based on its ID:
        {"id": 1}
    '''
    if request.method == 'POST':
        try:
            jsondata = json.loads(request.body)
            delete_validator = JSONSchemaValidator(validation_schema.DELETE_SPENDING_SCHEMA)
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


def updatespending(request) -> HttpResponse:
    '''
    POST endpoint
    Update a spending based on its ID, submit data JSON template:
        {"id": 1, "amount": 100, "currency": "USD", "reason": "shopping" // nullable, "date": 1598444361 // UNIX epoch}
        All fields are mandatory.
    '''
    if request.method == 'POST':
        try:
            jsondata = json.loads(request.body)
            update_validator = JSONSchemaValidator(validation_schema.UPDATE_SPENDING_SCHEMA)
            update_validator.validate(jsondata)
            jsondata['currency'] = get_currency_id(jsondata['currency'])
            if not jsondata['currency']:
                return HttpResponse(json.dumps({'error': error.DATA_ERROR, 'msg': 'Invalid currency code!'}))
            jsondata['amount'] = int(jsondata['amount'] * 100)
            params = ['id', 'amount', 'currency', 'reason', 'date']
            data = [jsondata.get(param) for param in params]
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('api.fun_update_spending', data)
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
