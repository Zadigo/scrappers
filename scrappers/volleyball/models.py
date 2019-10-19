from collections import namedtuple, OrderedDict

# IMPROVE: Subclass a list instead?
class Player(namedtuple('Player', ['name', 'link', 'date_of_birth',
                         'age', 'height', 'weight', 'spike', 'block'])):
    """Player class used to create a volleyball player
    """
    __slots__ = ()

# TODO: Erase countries -- unnecessary at this stage
# COUNTRIES = ['arg-argentina', 'aze-azerbaijan', 'bra-brazil',
#             'bul-bulgaria', 'cmr-cameroon', 'can-canada',
#             'chn-china', 'cub-cuba', 'dom-dominican%20republic',
#             'ger-germany', 'ita-italy', 'jpn-japan', 'kaz-kazakhstan',
#             'ken-kenya', 'kor-korea', 'mex-mexico',
#             'ned-netherlands', 'pur-puerto%20rico', 'rus-russia',
#             'srb-serbia', 'tha-thailand', 'tto-trinidad%20%20tobago',
#             'tur-turkey', 'usa-usa']