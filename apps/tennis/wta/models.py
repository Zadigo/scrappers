"""These are series of helpers created to optimize the design
of the components for the JSON file.
"""

import re
import datetime

class Tournament(dict):
    """Object representing the details of a WTA tournament
    """
    def __init__(self, tour_id, tournament, date, level, surface, rank, seed, **kwargs):
        normalized_date = self.normalize_date(date)
        if kwargs:
            self.update(**kwargs)
        self.update(
            {
                'id': tour_id,
                'tournament': tournament,
                'country': self.parse_location(kwargs['tournament_location'])['country'],
                'date': str(normalized_date),
                'year': normalized_date.year,
                'level': self.clean(level),
                'surface': self.clean(surface),
                'rank': self.convert_integer(rank),
                'seed': self.convert_integer(seed)
            }
        )
    
    @staticmethod
    def normalize(value):
        """ Normalize a value by capitalizing, lowering
        and stripping the white spaces
        """
        if not value:
            return None
        names = value.split(' ')
        for name in names:
            names[names.index(name)] = name.lower().capitalize()
        return ' '.join(names).strip()

    @staticmethod
    def clean(value):
        """Strips any whitespaces"""
        return value.strip()

    @staticmethod
    def parse_location(value):
        """Parse the location in the string"""
        is_match = re.match(r'(?<!\\)[a-zA-Z]+', value)
        if is_match:
            items = is_match.groups()
            country = items[0]
            city = items[1].lower().capitalize() + ', ' + items[2].lower().capitalize()
        return {'country': country, 'city': city}

    @staticmethod
    def normalize_date(d):
        """Transforms a date such as `Mar 19 - Mar 21 2019` 
        becomes a standard date `2019-10-03`

        Parameters
        ----------

            d: a date written as `Mar 19 - Mar 21 2019`
            for the converter to work
        """
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        is_valid = re.match(r'^(\w+\s+\d+).*(\d{4})$', d)
        if is_valid:
            sticked_date = is_valid.group(1)
            year = is_valid.group(2)
            month, date = sticked_date.split(' ')
            month_number = months.index(month) + 1
            formatted_date = f'{year}-{month_number}-{date}'
        return datetime.datetime.strptime(formatted_date, '%Y-%M-%d')

    def parse_tour_name(self, tour_name, tour_or_country=False):
        """Get the tournament's name.

            1. The incoming tournament name should be formatted
                as such: ""

            2. In the case where the format might be different, an
            additional REGEX can be passed to refine the extraction.

            Subclass Tournament and overwrite this method.
        """
        try:
            # If the format does not come as '', we have
            # to protect the app from a ValueError because
            # it would not be to split the unexpected format
            tournament, country = tour_name.split(',', 1)
        except ValueError:
            print("[INFO:] The tournament name's format is unexpected. Searching for %s but got %s"
                    % ('test', tour_name))
            return None

        if tour_or_country:
            return self.normalize(tournament)
        else:
            return self.normalize(country)

    @staticmethod
    def convert_integer(value):
        """Converts an integer within a string to number
        """
        if not value:
            return None
        return int(value)

    @staticmethod
    def parse_integer_regex(value):
        if not value:
            return None
        # ex. \n              18
        # ex. \nSeed Entry: \n  18
        is_match = re.match(r'\s+(\[?\d+\]?)', str(value))
        if is_match:
            return int(str(is_match.group(1)).strip())
        else:
            # Case where the number is [4]
            try_pattern = re.match(r'\[?(\d+)\]?', str(value))
            if try_pattern:
                return int(str(try_pattern.group(1)).strip())
        return None

class TournamentMatch(Tournament):
    """Object representing the details of a WTA tournament
    tennis match.

    Parameters
    ----------

        match_round: Round 128, Round 64...

        result: W/L

        score: 6-1 6-1...

        rank: 1, 2...

        seed: 1, 2...

    Structure
    ---------

        {
            match_round: match_round,
            result: result,
            score: score,
            sets_played: two,
            first_set: W,
            rank: 1,
            seed: 1,
            opponent_details: []
        }

    `opponent_details` is a dict
    """
    def __init__(self, match_round, result, score, rank, seed):
        score = self.clean(score)
        match_round = self.clean(match_round)
        rank = self.convert_integer(rank)
        seed = self.convert_integer(seed)

        self.update(
            {
                'match_round': match_round,
                'result': self.clean(result),
                'score': score,
                'sets_played': self.sets_played(score),
                'first_set': self.first_set(score, result),
                'rank': rank,
                'seed': seed,
                'opponent_details': []
            }
        )
    
    @staticmethod
    def first_set(score, result):
        """A piece of logic that determines if the first set 
        was won or lost.

        Parameters
        ----------

        score : The final score e.g. 6-1 6-1

        result : The result of the match. Either `W` or `L`
        """
        if result == 'L':
            # 6-2 6-3
            # 7-5 6-3
            # 7-6(6) 6-4
            is_match = re.search(r'^((?:6|7)\-?\d+)', score)
            if is_match:
                return 'lost'
            else:
                # 2-6 6-3
                # 5-7 6-3
                # 6-7(6) 6-4
                is_match = re.search(r'^(\d+\-(?:6|7))', score)
                if is_match:
                    return 'won'
        elif result == 'W':
            is_match = re.search(r'^((?:6|7)\-?\d+)', score)
            if is_match:
                return 'won'
            else:
                is_match = re.search(r'^(\d+\-(?:6|7))', score)
                if is_match:
                    return 'lost'

    @staticmethod
    def sets_played(score):
        """A piece of logic that determines the number of sets
        that were played
        """
        # There are certain cases where there was literally
        # no sets played -; for example 2-1. In which case,
        # we need to deal with that

        patterns = [
            # 6-2 6-3
            # 7-5 6-3
            # 7-6(4) 7-6(4)
            r'^\d+\-\d+\(?\d?\)?\s+\d+\-\d+\(?\d?\)?$',
            # 6-7(6) 6-4 6-4
            # 6-4 3-6 7-5
            # 6-4 3-6 7-5
            # 7-6(4) 6-7(4) 7-6(4)
            r'^\d+\-\d+\(?\d?\)?\s+\d+\-\d+\(?\d?\)?\s+\d+\-\d+\(?\d?\)?$'
        ]
        for pattern in patterns:
            is_match = re.match(pattern, score)
            if is_match:
                pattern_index = patterns.index(pattern)
                if pattern_index == 0:
                    number_of_sets = 'two'
                else:
                    number_of_sets = 'three'
                break
            else:
                number_of_sets = 'two'
        
        return number_of_sets

class Player(TournamentMatch):
    """Object representing a tennis player:

    Parameters
    ----------

        name: Eugénie Bouchard, 

        country: CAN, 

        url_path: /url/to/eugenie


    Structure
    ---------

        {
            name: Eugénie Bouchard, 
            country: CAN, 
            url_path: /url/to/eugenie
        }
    """
    def __init__(self, name, country, url_path):
        self.update(
            {
                'name': self.normalize(name),
                'country': country,
                'url_path': url_path,
            }
        )


# w = Tournament('sezzf', 'Google', 'Mar 19-Mar 30, 2019', '', '', 345, 345)
# print(w)