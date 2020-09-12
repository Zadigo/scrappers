import logging

# logger = logging.basicConfig(
#     filename='debug.log', level=logging.DEBUG, format='%(levelname)s :: %(asctime)s %(message)s')
# logging.warning('This is a message')
# # logger.warning('This is a test')

# logger = logging.getLogger('Something')
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler = logging.FileHandler('something.log')
# handler.setLevel(logging.DEBUG)
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.warning('This is a test')


class Logs:
    """
    Base logger for all applications in scrappers
    """
    logger = None

    def __init__(self, name='Default', logfile_name='scrappers.log'):
        logger = logging.getLogger(name)
        formatter = logging.Formatter('%(levelname)s :: %(asctime)s - %(name)s - %(message)s')
        handler = logging.FileHandler(logfile_name)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    def __call__(self, name, logfile_name='scrappers.log'):
        self.__init__(name, logfile_name=logfile_name)
        return self.logger

default = Logs()
