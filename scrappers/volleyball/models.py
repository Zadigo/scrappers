from collections import namedtuple

# ENHANCEMENT: Subclass a list instead?
class Player(namedtuple('Player', ['name', 'link', 'date_of_birth',
                         'age', 'height', 'weight', 'spike', 'block'])):
    """Player class used to create a volleyball player
    """
    __slots__ = ()
