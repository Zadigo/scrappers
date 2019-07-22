# Scrappers

## Volleyball

The volleyball scrappers regroups effective tools that can be used to scrap the FiVb website. The tools were created in order to gather data concerning players or teams that may interest you.

### How to

You can scrap pages in various manners. First, by importing the `ParticipatingTeamsPage` class which allows you to parse all the participating teams of a competition.

This class in itelf is not extremely useful since it returns raw data of aggregated links and countries:

```
[
    (url, country),
    (...)
]
```

The base structure is then used to get the individual data of each players. In that regards, to get more precise data, that's whre the `IndividualTeamPage` class is more useful.

This class can be overriden if you wish to improve the way it works.

In the same manner the representation of this class is a type `dict`. In other words, this class its subclasses can be directly iterated upon.

### Parsing individual pages

To parse a page without outputing it to a file, simply just call the .team_page function.

```
team_page = IndividualTeamPage()
team_page.team_page()
```

There are various other ways to output the data outside of the terminal: .to_csv, .to_json and .to_txt.

The files can also be uploaded to AWS directly with the AWS implementation.


# User agents
## Adding
Import the `USER_AGENTS` list from scrappers.config.http.user_agent : `USER_AGENTS += [...]`.

# AWS

Scrappers implements and AWS class that allows you to upload files directly to a bucket.

```
from scrappers import aws

path = 'C:\\...'
aws.upload_from_loval(path, bucket_name)
```
