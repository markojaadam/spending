#!/usr/bin/env python3

import json
import glob
import os
import configparser
import re
import pdb

def _(x):
    if type(x) in [int, float]:
        return(str(x))
    if type(x) == str:
        if re.match("^{.*}$",x):
            return("'" + x.replace("'", '"') + "'")
        else:
            return("'%s'" % (x.replace("'", "''")))
    elif type(x) == bool:
        return(str(x).upper())
    elif not x:
        return('NULL')
    elif type(x) == list:
        return([_(i) for i in x])
    else:
        return(str(x))


def reformat_dict(d: dict):
    return dict([(k, [each if type(each) is not list else '{' + ', '.join(_(each)) + '}' for each in v]) for k, v in d.items() if k not in EXCLUDED_KEYS])


EXCLUDED_KEYS = ['names']

jsonfiles = glob.glob('../db/static/json/*.json')
table_config = configparser.ConfigParser()
table_config.read_file(open('../db/static/tables.ini'))

for jsonfile in jsonfiles:
    fname = os.path.basename(jsonfile)
    d = reformat_dict(json.loads(open(jsonfile).read()))
    # pdb.set_trace()
    try:
        tablename = table_config.get('TABLES', fname.replace('.json', '.*'))
        columns = table_config.get(tablename, 'columns[]').replace(' ', '').split(',')
        columns = ['"' + col + '"' for col in columns]
        sql_query = f"""INSERT INTO {tablename} ({', '.join(columns)})\nVALUES """
        sql_query += f',\n{" " * 7}'.join(["(" + ', '.join([_(int(k))] + _(v)) + ")" for k,v in d.items() if type(v) == list and k != 'names'])
        sql_query += "\nON CONFLICT (pkey_id) DO UPDATE SET\n" + ',\n'.join([f"{colname} = EXCLUDED.{colname}" for colname in columns if colname != 'pkey_id']) + ';'
        outfname = f'../db/static/{fname.replace(".json", ".sql")}'
        with open(outfname, 'w') as sqlfile:
            sqlfile.write(sql_query)
            print('Generated %s' % os.path.basename(outfname))
    except:
        print(f'Config not found for {fname}')
