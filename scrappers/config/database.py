try:
    import psycopg2
except ImportError:
    pass

import sqlite3

# class Fields:
#     def __init__(self, field_names=[], field_type=[]):
#         constructed_fields = []
        
#         if not field_names:
#             return []

#         if len(field_names) != len(field_type):
#             pass
        
#         for i in range(len(field_names)):
#             constructed_fields.append(field_names[i] + ' ' + field_type[i].upper())

#         sql_statement = ', '.join(constructed_fields)

#         setattr(self, 'sql_statement', sql_statement)


class Connector:
    def __init__(self, using='sqlite'):
        self.conn = sqlite3.connect('local.sqlite')
        self.cursor = self.conn.cursor()

        # c = psycopg2.connect(database='test', user='postgres', password='secret')
        # cursor = c.cursor()
        # cursor.execute('CREATE')

    def create_table(self, **kwargs):
        if not kwargs:
            raise ValueError

        if 'table_name' in kwargs:
            table_name = kwargs['table_name']

        if 'headers' in kwargs and isinstance(kwargs['headers'], (tuple, list)):
            headers = ', '.join(kwargs['headers'])

        sql = f'CREATE TABLE {table_name} ({headers})'
        try:
            self.cursor.execute(sql,)
        except sqlite3.DatabaseError:
            raise
        else:
            self.conn.commit()
        print('Successfully created table %s!' % table_name)
        self.cursor.close()


# Connector().create_table(table_name='players', headers=['name TEXT', 'surname TEXT'])
# Connector().create_table(table_name='players', headers=['name TEXT', 'surname TEXT'])
