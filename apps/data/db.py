import sqlite3

class Manager:
    def get(self, **kwargs):
        pass
    
    def delete(self, **kwargs):
        pass
    
class BaseDabatabase(type):
    """The base class for using the applications with an sqlite
    database. You should not subclass this class directly but
    use the Models class instead.
    """
    def __new__(cls, name, bases, cls_dict):
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
                    database_name = name.lower() + '.lite'

            conn = sqlite3.connect(database_name)
            cursor = conn.cursor
            # Create the table and all the necessary
            # configurations for the database
            cls.create_table(cursor=cursor, fields=cls_dict['fields'])
            # For every model created, we put the
            # actual connection and the cursor in
            # the body of the class
            setattr(new_class, 'connection', conn)
            setattr(new_class, 'cursor', cursor)
        return new_class

    @staticmethod
    def create_table(**kwargs):
        if 'cursor' in kwargs:
            # .. cursor() method
            return kwargs['cursor']().execute('')

class Database(metaclass=BaseDabatabase):
    # Base manager for manipulating
    # objects within the database
    manager = Manager()

    def __init__(self, **kwargs):
        # Special method that initializes the
        # manager with the database in order
        # to start manipulating the latter
        self.manager.__dict__['cursor'] = None

class Models(Database):
    db_name = None
    fields = []

    def __setattr__(self, name, value):
        # Make sure the name that is provided
        # follows the pattern: name.sqlite if a
        # name was provided to name the database
        if name == 'db_name' and name is not None:
            try:
                name, extension = name.split('.')
            except Exception:
                raise Exception()
            else:
                if name and extension:
                    return super().__setattr__(name, value)

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
        return self.conn().commit()



class MyDatabase(Models):
    db_name = 'local.sqlite'
    fields = ['name', 'age']
