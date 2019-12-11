from scrappers.apps.images import base

url = 'https://www.sawfirst.com/adriana-lima-booty-in-bikini-on-the-beach-in-miami-2019-08-14.html/supermodel-adriana-lima-wears-a-tiny-string-bikini-as-she-hits-the-beach-in-miami-2'
r = base.SawFirst(url, celebrity_name='Adrianna Lima', div_id='')
print(r[0])