import os

from scrappers.engine.aws import AWS, TransferManager

environment = os.environ

class Configuration:
    def __init__(self):
        # Base path of 
        # the file being called
        self.base_path = os.path.abspath(__file__)

        # User homedrive
        self.homedrive = '%s\\Users\\%s\\Documents' % (
            environment.get('HOMEDRIVE'),
            environment.get('USERNAME')
        )

        # Output paths
        self.output_paths = [
            {
                'default': {
                    'path': os.path.join(self.homedrive, 'scrapper_data')
                }
            }
        ]

        # Amazon S3
        self.bucket = TransferManager

    def __unicode__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return self.__unicode__()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setattr__(self, name, value):
        if name == 'output_paths':
            if not isinstance(value, list):
                raise TypeError()
                # if not isinstance(value, dict):
                #     print('The path should be a valid dictionnary')
                #     raise TypeError()

                # if not 'path' in value:
                #     print('Path was not found in dictionnary')
                #     raise KeyError()

        # if name == 'bucket':
        #     value = self.bucket_is_callable(value)

        return super().__setattr__(name, value)

    # @classmethod
    # def bucket_is_callable(cls, obj):
    #     if callable(cls.bucket):
    #         return obj
        
    #     print('The bucket should be a callable object to use')
    #     raise TypeError()

configuration = Configuration()
