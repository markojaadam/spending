#!/usr/bin/env python3

from debug_core import *
import click
import texttable as ttbl

DEBUB_OPTIONS = click.Choice(['silent', 'all', 'submit', 'payload', 'errors'])

@click.group()
def cli():
    pass


@click.command()
@click.option('--order-by', type=click.Choice(['amount', 'currency', 'date']))
@click.option('--currency')
@click.option('--debug', type=DEBUB_OPTIONS, default='silent', show_default=True)
def get_spending(order_by, currency, debug):
    payload = get_spending_command(order_by, currency, debug)
    results = payload.get('data')
    if results:
        for i,each in enumerate(results):
            results[i]['date'] = pretty_date(results[i]['date'])
            results[i]['reason'] = results[i]['reason'] if results[i]['reason'] else ''
        t = ttbl.Texttable()
        t.set_deco(ttbl.Texttable.HLINES)
        t.add_row(list(results[0].keys()))
        for result in results:
            t.add_row(list(result.values()))
        print(t.draw())


@click.command()
@click.option('--amount', type=int)
@click.option('--currency')
@click.option('--reason')
@click.option('--date', type=int, default=int(time.time()) - 3600, show_default=True)
@click.option('--debug', type=DEBUB_OPTIONS, default='silent', show_default=True)
def add_spending(amount, currency, reason, date, debug):
    add_spending_command(amount, currency, reason, date, debug)


@click.command()
@click.option('--id', type=int)
@click.option('--debug', type=DEBUB_OPTIONS, default='silent', show_default=True)
def delete_spending(id, debug):
    delete_spending_command(id, debug)


@click.command()
@click.option('--id', type=int)
@click.option('--amount', type=int)
@click.option('--currency')
@click.option('--reason')
@click.option('--date', type=int)
@click.option('--debug', type=DEBUB_OPTIONS, default='silent', show_default=True)
def update_spending(id, amount, currency, reason, date, debug):
    payload = get_spending_command(None, None, 'silent')
    spending_data = payload.get('data')
    spending = [s for s in spending_data if s.get('id') == id]
    if spending:
        my_spending = spending[0]
        amount = amount if amount else my_spending.get('amount')
        currency = currency if currency else my_spending.get('currency')
        reason = reason if reason else my_spending.get('reason')
        date = date if date else my_spending.get('date')
        update_spending_command(id, amount, currency, reason, date, debug)
    else:
        click.echo('Spending not found.')


cli.add_command(get_spending)
cli.add_command(update_spending)
cli.add_command(delete_spending)
cli.add_command(add_spending)

if __name__ == "__main__":
    cli()
