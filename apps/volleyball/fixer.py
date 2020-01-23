import pandas
import datetime

PATH = 'C:\\Users\\Pende\\Documents\\myapps\\scrappers\\apps\\volleyball\\japan_2018.csv'

#%%
data = pandas.read_csv(PATH)
df = pandas.DataFrame(data=data)

#%%
def age_in_x(year):
    """Calculates the player's age at a given year"""
    def calculate(value):
        date_of_birth = datetime.datetime.strptime(value, '%d/%m/%Y')
        age = year - date_of_birth.year
        return age
    return calculate

df['age_in_2018'] = df['date_of_birth'].apply(age_in_x(2018))

#%%
# Get spikes and blocks that are not 0 to calculate
# the average and apply them to data with zero
data_not_zero = df[(df['block'] != 0) & (df['spike'] != 0)]
spike_average = data_not_zero['spike'].mean()
block_average = data_not_zero['block'].mean()

def transform_to_average(column):
    def transform(value):
        if value == 0 and column == 'spike':
            return round(spike_average, 0)
        elif value == 0 and column == 'block':
            return round(block_average, 0)
        else:
            return value
    return transform

df['spike'] = df['spike'].apply(transform_to_average('spike'))
df['block'] = df['block'].apply(transform_to_average('block'))

#%%
# Reprint file to csv
df.to_csv('japan_2018_fixed.csv')