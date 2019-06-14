# %%
import pandas

# %%
url = 'https://raw.githubusercontent.com/Zadigo/scrappers/master/tennis/WTA/matches.json'
data = pandas.read_json(url, orient='records', convert_dates=True)
df = pandas.DataFrame(data)
print(df)