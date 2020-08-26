#!/usr/bin/env python3

sql_file = open('../db/tbl.sql').read().split('\n')
seq_index = sql_file.index('-- sequences')
table_index = sql_file.index('-- tables')
end_index = sql_file.index('-- End of file.')
newsql= sql_file[0:table_index] + sql_file[seq_index:end_index] + sql_file[table_index:seq_index] + sql_file[end_index:]
newsql = ('\n').join(newsql)
with open('../db/tbl.sql', 'w') as file:
    file.write(newsql)
