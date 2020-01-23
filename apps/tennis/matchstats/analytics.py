import json
import csv

PATH = 'C:\\Users\\Pende\\Documents\\myapps\\scrappers\\apps\\tennis\\matchstats\\eugenie_bouchard_stats.json'

def addition(func):
    """A decorator that ouputs the sum of a set of values"""
    def addition_result(self, opponent=False):
        return sum(func(self, opponent=opponent))
    return addition_result

def percentage(func):
    """A decorator that beautifies the output for percentage or ratio values"""
    def fix(self, round_by):
        return round(func(self), round_by)
    return fix

def average(func, round_by):
    def average_result(self, opponent=False):
        values = func(self, opponent=opponent)
        return sum(values) / len(values)
    return round(average_result, round_by)


class Analytics:
    """A simple class created in order to analyse a statistics
    file with functions such as sum, average etc.
    """
    def __init__(self, filepath, player):
        with open(filepath, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            records = data['records']

        # All the data
        self.data = data
        # Represents a list of records 
        # referenced by their respective iD
        self.records = records
        self.player = player

        self.player_data = []
        self.opponent_data = []

        self.headers = self.create_headers(self.records[0])
        # All the data of 
        # a specific player
        for record in self.records:
            player_stats = record['stats']
            for player_stat in player_stats:
                if 'player_fullname' in player_stat:
                    if player_stat['player_fullname'] == player:
                        self.player_data.append(player_stat)
                    else:
                        self.opponent_data.append(player_stat)

    # def sum_winners(self, opponent=False):
    #     """Total of the winners for a given player or for the opponent"""
    #     return sum(self.iterator('winners'))

    # def sum_unforced_errors(self, opponent=False):
    #     """Total of all the unforced errors for a given player or for the opponent"""
    #     return sum(self.iterator('unforced_errors'))

    # def sum_points_won(self, opponent=False):
    #     """Total of points won for a given player or for the opponent"""
    #     return sum(self.iterator('points_won', opponent=opponent))

    # def grand_total_points(self):
    #     """Sums the total points of all the matches"""
    #     return sum(self.list_key_values('total_points'))

    # def ratio_winner_unforced(self, opponent=False):
    #     """A ratio between winners and unforced errors for a given player or for the opponent

    #     Calculus
    #     --------

    #         winners / unforced
    #     """
    #     ratio = int(self.sum_winners())/int(self.sum_unforced_errors())
    #     return round(ratio, 3)

    # def winner_unforced_margin(self, opponent=False):
    #     """The difference between winners and unforced errors

    #     Caculus
    #     -------
            
    #         winners - unforced

    #         If the player stroke more winners than unforced, then the margin
    #         is positive. Otherwise, it's negative.
    #     """
    #     return self.sum_winners() - self.sum_unforced_errors()

    # # def margin_on_total_points(self, opponent=False):
    # #     """"""
    # #     return self.winner_unforced_margin() / self.sum_points_won()

    # def percentage_of_winners(self, opponent=None):
    #     """Returns share of winners within the total points won by a player
        
    #     Calculus
    #     --------

    #         winners / total_points_won
    #     """
    #     return round(self.sum_winners() / self.sum_points_won(), 4)

    # def percentage_of_unforced(self, opponent=None):
    #     """Returns share of winners within the total points won by a player
        
    #     Calculus
    #     --------

    #         winners / total_points_won
    #     """
    #     return round(self.sum_unforced_errors() / self.sum_points_won(opponent=True), 4)

    # def forced_winners(self):
    #     pass

    # def forced_errors(self):
    #     pass

    # def aggressive_margin(self):
    #     pass

    # def register_stats(self):
    #     advanced_stats = {
    #         'sum_winners': self.sum_winners()
    #     }
    #     self.data['advanced_stats'] = advanced_stats
    #     print(self.data)

    # def player_stats_to_csv(self):
    #     """Outputs the current selected player's statistics to a
    #     CSV file
    #     """
    #     row = []
    #     with open('', 'r', encoding='utf-8', newline='') as f:
    #         csv_writer = csv.writer(f)
    #         for data in self.player_data:
    #             for header in self.headers:
    #                 row.append(data[header])
    #             csv_writer.writerow(row)

    def list_key_values(self, key):
        """Return all the values for a given key"""
        values = []
        for item in self.records:
            # For the total points, we must not add
            # the one for the player and the one for the
            # opponent -- we only need one.
            if key == 'total_points':
                values.append(item['stats'][0][key])
            else:
                stat = item['stats'][0][key], item['stats'][1][key]
                values.append(stat)
        return values

    # def grand_winners(self):
    #     """Sums the amount of winners of all the matches"""
    #     winners = 0
    #     for value in self.list_key_values('winners'):
    #         winners = winners + value
    #     return winners

    # def match_winners_percentage(self):
    #     """Calculates the percentage of winners of both players in the match"""
    #     return sum(self.list_key_values('total_points'))

    @staticmethod
    def create_headers(sample_data:dict):
        """Returns the keys of the dict as list"""
        return sample_data['stats'][0].keys()

    @staticmethod
    def simple_iterator(values:list, opponent=False):
        """An iterator that receives an array composed of a pair of
        values which returns the value based on a given index
        """
        # We'll return the player's data
        # from the get-go unless specified
        # otherwise
        index = 1
        if opponent:
            index = 0
        items = [value[index] for value in values]
        return items

    def complex_iterator(self, key, opponent=False):
        """An iterator that analyses the keys in the dict to return their
        values as a list
        """
        values = []
        if not opponent:
            stats = self.player_data
        else:
            stats = self.opponent_data
        for stat in stats:
            try:
                values.append(stat[key])
            except KeyError:
                raise
            else:
                return values

    @staticmethod
    def substract(a, b):
        return a - b

    @staticmethod
    def divide(a, b):
        return a / b

    def as_csv_format(self, advanced_stats=False):
        base = []
        row = []
        headers = list(self.headers)
        if advanced_stats:
            headers.append('contribution_margin')
            headers.append('ratios')
        base.append()
        for data in self.player_data:
            for key in self.headers:
                row.append(data[key])
                if advanced_stats:
                    row.append(self.substract(data['winners'], data['unforced_errors']))
                    row.append(self.divide(data['winners'], data['unforced_errors']))
            base.append(row)
        return base

class Matches(Analytics):
    """Aggregates statistics for a single match"""
    @property
    def list_winners(self):
        """List all the winners for a player"""
        winners = [data['winners'] for data in self.player_data]
        return winners

    @property
    def list_unforced(self):
        """List all the unforced errors for a player"""
        winners = [data['unforced_errors'] for data in self.player_data]
        return winners

    """Aggregates statistics for all the matches"""
    @addition
    def winners(self, opponent=False):
        """Global sum of winners"""
        return self.simple_iterator(self.list_key_values('winners'), opponent=opponent)

    @addition
    def unforced(self, opponent=False):
        """Global sum of unforced"""
        return self.simple_iterator(self.list_key_values('unforced_errors'), opponent=opponent)

    @addition
    def total_points(self):
        """Global sum of points won"""
        return self.list_key_values('total_points')
    
    @percentage
    def winners_pct(self):
        pass

    @percentage
    def unforced_pct(self):
        pass

    def winners_avg(self):
        return self.list_key_values('winners')

    def unforced_avg(self):
        pass

    @addition
    def forced_errors(self):
        pass

    def forced_winners(self):
        pass

    def forced_winners_pct(self):
        pass

    def forced_errors_pct(self):
        pass

    def aggressive_margin(self):
        pass

    def true_winners(self):
        pass

    def true_unforced(self):
        pass

    def relative_strength(self):
        pass

    def contribution_margin(self):
        pass

    def contribution_margins(self):
        margins = []
        winners = self.list_winners
        unforced = self.list_unforced
        for i in range(len(winners)):
            margins.append(winners[i] - unforced[i])
        return margins


class Match(Analytics):
    pass

# element = Analytics(PATH, 'Eugenie Bouchard')
m = Matches(PATH, 'Eugenie Bouchard')
print(m.contribution_margins())
