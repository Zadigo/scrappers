class Messages:
    """Base classed used to generate messages for scrappers
    """
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return '[%s]: %s' % (self.__class__.__name__, self.message)

    def __str__(self):
        return '[%s]: %s' % (self.__class__.__name__, self.message)

    def __unicode__(self):
        return self.__str__()

    @property
    def context(self):
        return {'class': f'{self.__class__.__name__.lower()}', 'message': self.message}

class Info(Messages):
    pass

class Error(Messages):
    pass

class Warning(Messages):
    pass
