# TODO: Erase countries -- unnecessary at this stage
# COUNTRIES = ['arg-argentina', 'aze-azerbaijan', 'bra-brazil',
#             'bul-bulgaria', 'cmr-cameroon', 'can-canada',
#             'chn-china', 'cub-cuba', 'dom-dominican%20republic',
#             'ger-germany', 'ita-italy', 'jpn-japan', 'kaz-kazakhstan',
#             'ken-kenya', 'kor-korea', 'mex-mexico',
#             'ned-netherlands', 'pur-puerto%20rico', 'rus-russia',
#             'srb-serbia', 'tha-thailand', 'tto-trinidad%20%20tobago',
#             'tur-turkey', 'usa-usa']


class EnrichPlayer:
    def __init__(self, player_name):
        try:
            from googlesearch import search, search_images
        except ImportError:
            raise

        # response = search(player_name, stop=5, pause=2)
        response = search_images(player_name, stop=5, pause=2, extra_params={'biw':1024,'bih':768})


# if __name__ == "__main__":
#     args = argparse.ArgumentParser(description='FiVB page parser')
#     args.add_argument('-u', '--url', help='URL to query')
#     args.add_argument('-a', '--adjust-age', type=int, help='Adjust age to the year the tournament was played')
#     args.add_argument('-o', '--output_filename', help='Name to associate with the CSV file')
#     parsed_args = args.parse_args()

#     # if parsed_args.output_filename:
#     # data = TeamPage(url=parsed_args.url)
#     # data.get_team_page()

#     data = TeamPage(url=parsed_args.url)
#     data.get_team_page()

#     # PlayerPage('https://www.volleyball.world/en/vnl/women/teams/ita-italy/players/cristina-chirichella?id=71297')


# TODO: Delete this method
# def get_countries(self, path):
#     """Return the countries with their paths
#     present on a team's page.
#     '/en/vnl/women/teams/dom-dominican%20republic'
#     """
#     relative_link = unquote(path)
#     country = re.search(r'\w+\-(\w+\s?\w+)', relative_link)
#     if country:
#         return (country.group(1).capitalize(), path)
#     return None
