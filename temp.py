from scrappers.apps.images import base
from scrappers.apps.config.http.utilities import asynchronous_requests
from scrappers.apps.data.db import Models

# url = 'https://www.sawfirst.com/adriana-lima-booty-in-bikini-on-the-beach-in-miami-2019-08-14.html/supermodel-adriana-lima-wears-a-tiny-string-bikini-as-she-hits-the-beach-in-miami-2'
# r = base.SawFirst(url, celebrity_name='Adrianna Lima', div_id='')
# print(r.download_images())

# url = 'https://www.sawfirst.com/wp-content/uploads/2019/12/Kendall-Jenner-Booty-507-scaled.jpg'
# asynchronous_requests(url)

# class MyDatabase(Models):
#     db_name = 'local'
#     fields = ['name', 'age']

#     using = 'sqlite'
#     plural = 'locals'

#     class Meta:
#         something = 'A'

#     def test(self):
#         pass

class Celebrity(Models):
    db_name = 'celebrities'
    fields = ['name', 'image']
    plural = 'celebrities'

    class Meta:
        pass

base.SawFirst('', model=Celebrity)