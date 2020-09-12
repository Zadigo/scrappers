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

    [(url, country), (...)]
```

There are various other ways to output the data outside of the terminal: .to_csv, .to_json and .to_txt.

The files can also be uploaded to AWS directly with the AWS implementation.


# Images

## Introduction

The general flow for downloading specific set of images from a website is the following:

```
scrapper = ImageDownloader(__file__, url="https://website.com")
scrapper.build("name-to-filter")
```

If you prefer using a downloaded HTML page do:

```
scrapper = ImageDownloader(__file__, html_page="path/to/page")
scrapper.build("name-to-filter")
```

### Using the lookup method

When the ImageDownloader is initiated, it looks up for any `.html`, `.csv` and `.config` files present in the current directory. By doing so, you can then look up a specific file using the custom method.

```
scrappers.lookup("test.html", just_path=True)
```

By looking up an HTML file, the `.html_path` attribute of the class is automatically set to the looked up file and calling build will then use that file automatically for any image parsing.

This example for instance, will inititalize the class with the url provided for downloading the images on the current page.

```
scrapper = ImageDownloader(__file__, url="https://www.sawfirst.com/kendall-jenner-booty-out-for-coffee-in-malibu-2020-09-11.html")
```

## Dowloading the images

To download the corresponding imges, you need to build the request by filtering out the images with a specific element in the src or url.

You an also pass an optional regex that will replace the matched element with a specific string. By default, the replacement string will be `.jpg` if nothing is provided.

For instance, let's say we want to get all images that contains  `kendall-jenner-booty-out` in their url. We would so something like this:

```
scrapper.build("Brooke-Burke-Booty")

# Alternatively you can check the urls that were retrieved

scrapper.urls

    >> [ ... ]


scrapper.get_urls

    >> [ ... ]
```

Now, some image url might have a specific structure especially for thumbnails in lieu and place of the original full size image.

That's where the `regex` and `replace_with` parameters come in handy. __They will replace any matched item with the new string that you provided__ in order to get the original item to download.

For example, let's take our previous url `https://.../kendall-jenner-booty-out-for-coffee-in-malibu-2020-09-11-130x170.jpg` but this time, the thumbnail version of it. By using the regex replacement parameter, we can get the following `https://www.sawfirst.com/kendall-jenner-booty-out-for-coffee-in-malibu-2020-09-11.jpg` which points to the original size image.

```
scrapper.build("Brooke-Burke-Booty", regex=r'\-130x170.jpg')
```

By default all downloads are made in a directory `..\\images\\Images\\scrappers` but can be substituted by another one like so:

```
scrapper.images_dir = "\\path\\to\\directory"
```

## Saving

### images urls

You can save the list of images urls that you have parsed from the website by calling the `save_links` method:

```
scrapper.save_links(filename="custom_name", file_type="csv")
```

The two supported file types are csv and json.

## Loading

Once you have saved the set of link, you can easily reload them in memomy like so:

```
scrapper.load("/path/")
```

# AWS

Scrappers implements and AWS class that allows you to upload files directly to a bucket.

```
from scrappers import TransferManager

path = 'C:\\...'
manager = TransferManager(access_key, secret_key, region, bucket)
manager.upload_from_local(path, bucket_name)
```
