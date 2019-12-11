import sqlite3
import psycopg2
from string import Template

class Cache:
    def __init__(self, queryset):
        if isinstance(queryset, dict):
            self.queryset = queryset.copy()

    @property
    def from_cache(self):
        return self.queryset

    def __repr__(self):
        return self.queryset

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return self.from_cache

class Functions:
    pattern = '%s (%s)'
    test_pattern = Template('INSERT INTO $ VALUES($)')

    def deconstruct(self, **kwargs):
        """Deconstructs a query into a readable sql
        statement for the database

        Description
        -----------

            Users will often query the database using techniques
            such as get(name__iexact="value").
            
            The deconstruct() method will separate the query in parts such as
            column_name (name) and conditions (iexact...) can
            be transformed into sql statements
        """
        if len(kwargs) == 1:
            if '__' in kwargs:
                items = kwargs.keys()


    def reconcile(self, statement, conditions=None, **kwargs):
        """Reconciles an sql statement with the values
        """
        # Deconstruct the incoming statement
        # in order to create the remaining 
        # SQL statement
        parts = self.deconstruct(**kwargs)
        if statement == 'SELECT':
            pattern = f'{statement} FROM {statement}'

        return pattern

class Manager(Functions):
    def __init__(self):
        self.sql_stack = []

    def append(self, sql):
        return self.sql_stack.append(sql)

    def _all(self):
        pass

    def _filter(self):
        return Cache({})

    def get(self, **kwargs):
        return self.reconcile('SELECT', **kwargs)
    
    def delete(self, **kwargs):
        pass
    
class BaseDabatabase(type):
    """The base class for using the applications with an sqlite
    database. You should not subclass this class directly but
    use the Models class instead.
    """
    def __new__(cls, name, bases, cls_dict):
        # print(cls_dict)
        new_class = super().__new__(cls, name, bases, cls_dict)
        if name != 'Database' and name != 'Models':
            try:
                database_name = cls_dict['db_name']
            except KeyError:
                pass
            else:
                # If we did not provide an explicit
                # database name, then we need to get
                # the name of the database from the name
                # of the class that was used to create the model
                if name is None:
                    database_name = name.lower()
            if 'using' in cls_dict:
                if cls_dict['using'] == 'postgres':
                    connection_items = cls.connect_database(database_name, database='', user='', password='')
                else:
                    connection_items = cls.connect_database(database_name)

            # conn = sqlite3.connect(database_name)
            # cursor = conn.cursor
            conn = connection_items[0]
            cursor = connection_items[1]
            # Create the table and all the necessary
            # configurations for the database
            cls.create_table(cursor=cursor, fields=cls_dict['fields'])
            # For every model created, we put the
            # actual connection and the cursor in
            # the body of the class
            setattr(new_class, 'connection', conn)
            setattr(new_class, 'cursor', cursor)

            # Check for Meta elements in the class
            # and work on them here
            if 'Meta' in cls_dict:
                # Get the dict of the class and its
                # attributes for models creation
                klass_dict = cls_dict['Meta'].__dict__
                accepted_attributes = ['something']
                for key in klass_dict.keys():
                    if not key.startswith('__') and \
                             key not in accepted_attributes:
                        raise AttributeError('The attribute "%s" you provided for the Meta in model "%s" is not valid.' % (key, name))
        return new_class

    @classmethod
    def connect_database(cls, database_name, backend='sqlite', **kwargs):
        """Creates and returns a connection to a given database using the
        default backend or a user provided backend
        """
        conn = None
        if backend == 'sqlite':
            full_name = '.'.join([database_name, backend])
            conn = sqlite3.connect(full_name)
            cursor = conn.cursor
        elif backend == 'postgres':
            if not 'database' in kwargs and not 'user' in kwargs and not 'password' in kwargs:
                raise Exception('You did not provide any credentials for connecting to Postgres: database, user and password')
            conn = psycopg2.connect(database='', user='', password='')
            if not conn:
                raise psycopg2.DatabaseError()
            cursor = conn.cursor
        elif backend == 'mongodb':
            pass
        return conn, cursor

    @staticmethod
    def create_table(**kwargs):
        if 'cursor' in kwargs:
            # .. cursor() method
            return kwargs['cursor']().execute('')

class Database(metaclass=BaseDabatabase):
    # Base manager for manipulating
    # objects within the database
    manager = Manager()

class Models(Database):
    db_name = None
    fields = []

    def __setattr__(self, name, value):
        if name == 'fields':
            if not isinstance(name, (list, tuple)) \
                    or name is None:
                raise TypeError()
            else:
                return super().__setattr__(name, value)

        return super().__setattr__(name, value)
            
    def save(self, **kwargs):
        """Commits the data to the database
        """
        pass




class MyDatabase(Models):
    db_name = 'local'
    fields = ['name', 'age']

    using = 'sqlite'
    plural = 'locals'

    class Meta:
        something = 'A'

    def test(self):
        pass

print(MyDatabase().manager.get())