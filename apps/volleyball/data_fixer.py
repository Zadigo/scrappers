#%%
import pandas
import os
# from scrappers.volleyball import base_volleyball
import datetime
import re
from urllib.parse import unquote
import csv

#%%
file_path = os.path.join('C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\volleyball\\data', '6_2019_b98aa9abb8.csv')
data = pandas.read_csv(file_path, sep=',', date_parser=True)

#%%
columns = ['name', 'profile_page', 'date_of_birth', 'age', 'height', 'weight', 'spike', 'block']
df = pandas.DataFrame(data, columns=columns)

#%%
# Analysis
df.describe()
df.shape

#%%
# 01/08/1997 -> 01-08-1997
def change_date(d):
    date = datetime.datetime.strptime(d, '%d/%m/%Y')
    new_date = f'{date.day}-{date.month}-{date.year}'
    return new_date

df['date_of_birth'] = df['date_of_birth'].apply(change_date)

#%%
# New country column
def collect_country(link, full_country=False):
    link = unquote(link)
    # country: can-canada or dom-republic dominica
    country = re.search(r'(?<=\/)([a-z]{3})\-(\w+\s?\w+)(?=\/)', link)
    if country:
        if full_country:
            return country.group(2).capitalize()
        else:
            return country.group(1).upper()

def collect_player_id(link):
    link = unquote(link)
    fivb_id = re.search(r'(?<=\?)id\=(\d+)$', link)
    return fivb_id.group(1)

df['country_code'] = df['profile_page'].apply(collect_country)
df['fivb_id'] = df['profile_page'].apply(collect_player_id)

#%%
def recalculate_age(date_of_birth):
    """Recalculate age to the year when the tournament
    was actually played.
    """
    formatted_date = datetime.datetime.strptime(date_of_birth, '%d-%m-%Y')
    true_age = 2017 - formatted_date.year
    return true_age

df['age_at_time'] = df['date_of_birth'].apply(recalculate_age)
df[:5]

#%%
# df.to_csv(os.path.join(DATA_DIR, 'test.csv'), sep=',')

#%%
def create_country_file():
    countries = df['country_code'].drop_duplicates()
    with open(os.path.join(DATA_DIR, 'countries.csv'), mode='w', encoding='utf-8', newline='') as f:
        csv_file = csv.writer(f)
        i = 1
        for country in countries:
            csv_file.writerow([country, i])
            i+=1

# create_country_file()
