"""These are series of helpers created to optimize the design
of the components for the JSON file.
"""

import re

class Tournament(dict):
    """Object representing the details of a WTA tournament
    """
    def __init__(self, tour_id, tournament, date, level, surface, rank, seed, **kwargs):
        self.update(
            {
                'id': tour_id,
                'tournament': self.parse_tour_name(tournament, tour_or_country=True),
                'country': self.parse_tour_name(tournament),
                'date': self.normalize_date(date),
                'level': self.normalize(level),
                'surface': self.normalize(surface),
                'rank': self.parse_integer_regex(rank),
                'seed': self.parse_integer_regex(seed)
            }
        )
    
    @staticmethod
    def normalize(value):
        """ Normalizes names `eugenie bouchard\\s` to `Eugenie Bouchard`
        """
        if not value:
            return None
        # DELETE: Old way of normalizing values
        # return value.strip().lower().capitalize()
        names = value.split(' ')
        for name in names:
            names[names.index(name)] = name.lower().capitalize()
        return ' '.join(names).strip()

    @staticmethod
    def normalize_date(d):
        """Transforms a date such as `October 3rd, 2019` to `2019-10-03`.

        Parameters
        ----------

        `d` should be a date written as `October 3rd, 2019` for the converter
        to work. If not, returns null
        """
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']
        is_valid = re.match(r'^([A-Z]\w+)\s+(\d+)\S\s+(\d+)', d)
        if is_valid:
            day = is_valid.group(2)
            month = is_valid.group(1).strip()
            year = is_valid.group(3)
            month_index = months.index(month) + 1
            formatted_date = f'{year}-{month_index}-{day}'
        return formatted_date

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
    def parse_integer(value):
        """Converts/parses an integer from `"1"` to `1`.
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
        score = self.normalize(score)
        match_round = self.normalize(match_round)
        rank = self.parse_integer_regex(rank)
        seed = self.parse_integer_regex(seed)

        self.update(
            {
                'match_round': match_round,
                'result': result,
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