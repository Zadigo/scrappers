import os
import secrets
from mimetypes import guess_extension, guess_type

import boto3


def image_size_creator(image_or_path):
    """
    Create three different types of image sizes for the
    S3 bucket. The original one, small, medium and large.
    """
    # If local path, we need to get 
    # the basename
    if os.path.isfile(image_or_path):
        name, extension = os.path.basename(image_or_path).split('.', 1)
    else:
        # Otherwise, just split the element
        name, extension = image_or_path.split('.', 1)

    images_sizes = {
        'original': name,
        'small': name + '-small',
        'medium': name + '-medium',
        'large': name + '-large'
    }

    # Append the extension
    for key, value in images_sizes.items():
        images_sizes.update({key: value + '.' + extension})
    
    # Put the content type in case we would need it
    images_sizes.update({'contenttype': guess_type(image_or_path)})

    return images_sizes

def create_object_url(object_path, region=None, bucket=None):
    """
    Create a base url for an object that was previously
    created in a bucket in order to save it to a local
    database for example.
    
    The general settings `AWS_REGION`
    can be overriden with the `region` and so as the bucket

    `object_path` should be the relative path of the object
    in the bucket such as `folder/object.ext` or `folder/folder/object.ext`

    Example link
    ------------

    -https://s3.eu-west-3.amazonaws.com/jobswebsite/banners/object.jpg-
    """
    # region = region or AWS_REGION
    # bucket = bucket or AWS_BUCKET

    return f'https://s3.{region}.amazonaws.com/{bucket}/{object_path}'

def unique_path_creator(folder, filename, rename=False):
    """
    Create a unique path for an object to be stored
    in an AWS bucket. Returns a dictionnary with the
    object's new name, path and url.

    Parameters
    ----------

    `folder` is the folder to access within the bucket. You can
    use a path such as path/to/

    `filename` is the name of the file

    `rename` allows you to rename the file to a random name

    Description
    -----------

        {
            'object_name': ['name', ('image/jpeg', None)], 
            'object_path': 'path/to/file.jpg',
            'object_url': 'https://s3...',
            'unique_entry': 'acc318515f364f1d37ecac456e6365bc1e4ae216'
        }

        unique_entry is the unique folder created in order to identify a set
        of files in your bucket
    """
    name, extension = filename.split('.', 1)

    unique_entry = secrets.token_hex(20)

    if rename:
        name = secrets.token_hex(10)
        extension = extension.lower()
    
    else:
        name = name.lower()
        extension = extension.lower()

    object_path = '%s/%s/%s.%s' % (folder, unique_entry, name, extension)
    # Create the objet's URL to save to a database for example
    # FIXME: Find a way to pass the bucket and the region
    object_url = create_object_url(object_path)
    
    return {'object_name': [name, guess_type(filename)], 'object_path': object_path, 
                'object_url': object_url, 'unique_entry': unique_entry}

class AWS:
    """This is the base used to connect to an AWS bucket.

    Parameters
    ----------
        
    `access_key` is the access key to the S3 account
    
    `secret_key` is the secret key to the S3 account
            
    `region` is the region of your bucket
    
    `bucket` is your bucket's name
    """
    def __init__(self, access_key, secret_key, region, bucket):
        session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        client = session.resource('s3', region_name=region)
        print('[%s]: Connection. Connected to %s' % (self.__class__.__name__, bucket))
        self.bucket = client.Bucket(bucket)

class QueryManager(AWS):
    def get_all(self):
        return [item for item in self.bucket.objects.all()]

    def get_folder(self, folder, choices=False):
        """Get the specific items of a folder

        Description
        -----------

        For example, let's return the folder ./test in a bucket:

            (
                ('test/', 'item'), 
                ('test/subfolder/to.jpg', 'item'), 
                ...
            )
        """
        obj = tuple((item.key, 'item') for item in self.bucket.objects.filter(Prefix=folder))
        return obj

    def get_folder_links(self, folder):
        """Get the specific items' links in a folder
        """
        objs = self.get_folder(folder)

        # Delete root path
        # e.g. (test/, item)
        # list(objs).pop(0)

        for obj in objs:
             yield create_object_url(obj[0], region='eu-west-3', bucket='jobswebsite')

    def get_file_url(self, root, path):
        """`root` main folder to use
        `path` is the path to the file
        """
        item = self.bucket.objects.filter(Prefix=root, Delimiter='/', Key='sophie.jpg')
        if item:
            # Reconcile the base path
            # with the relative one to
            # create a fully qualified
            # relative path 
            # ex. root/subfolder/to.jpg
            path = root + '/' + path
            return create_object_url(path, region='eu-west-3', bucket='jobswebsite')
        return None

    def delete_file(self, relative_path):
        """Deletes a file in the bucket

        Parameters
        ----------

        `relative_path` as fully qualified e.g. subfolder/path/to.jpg
        """
        obj = self.bucket.Object('test/3e7e208c6a3b27df0ca556e0f5d1207748e3f277/sophie.jpg')
        obj.delete()
        if isinstance(obj, dict):
            print('[%s]: Deletion. Deleted file, was %s' % (self.__class__.__name__, obj['VersionId']))
        return print('[%s]: Deletion. Object does not exist or is already deleted.' % self.__class__.__name__)

class TransferManager(AWS):
    def upload_from_post_request(self, file_to_upload, bucket, model=None, request=None):
        item_name = file_to_upload.name
        contenttype = file_to_upload.content_type

        items = unique_path_creator('test', item_name, rename=False)

        try:
            self.bucket.put_object(Key=items['object_path'], Body=file_to_upload, ACL='public-read',
                                        ContentType=contenttype[0], CacheControl='max-age=24000')

        except boto3.exceptions.S3TransferFailedError:
            print('[%s]: Upload failed. %s was not uploaded.' 
                    % (self.__class__.__name__, items['object_path']))

    def upload_from_local(self, file_to_upload, bucket, model=None, request=None):
        # We have to test weither the file comes from
        # a path or weither it comes from a form e.g. django
        is_local_file = os.path.isfile(file_to_upload)
        # No? It's a Django uploaded file
        if is_local_file:
            item_name = os.path.basename(file_to_upload)
            contenttype = guess_type(file_to_upload)

            with open(file_to_upload, 'rb') as f:
                data = f.read()

                # Create the paths
                items = unique_path_creator('test', item_name, rename=False)

                # Upload the file
                try:
                    self.bucket.put_object(Key=items['object_path'], Body=data, ACL='public-read',
                                                ContentType=contenttype[0], CacheControl='max-age=24000')
                except boto3.exceptions.S3TransferFailedError:
                    print('[%s]: Upload failed. %s was not uploaded.' 
                            % (self.__class__.__name__, items['object_path']))

    def from_local_to_existing(self, file_to_upload, folder_name='test/3e7e208c6a3b27df0ca556e0f5d1207748e3f277'):
        # We have to test weither the file comes from
        # a path or weither it comes from a form e.g. django
        is_local_file = os.path.isfile(file_to_upload)

        if is_local_file:
            item_name = os.path.basename(file_to_upload)
            contenttype = guess_type(file_to_upload)

            with open(file_to_upload, 'rb') as f:
                data = f.read()

                # Upload the file
                try:
                    response = self.bucket.put_object(Key=folder_name + '/' + item_name, Body=data, ACL='public-read',
                                                ContentType=contenttype[0], CacheControl='max-age=24000')
                except boto3.exceptions.S3TransferFailedError:
                    print('[%s]: Upload failed. %s was not uploaded.' 
                            % (self.__class__.__name__, item_name))
                else:
                    return response



    # def upload(self, file_to_upload, bucket, model=None, request=None):
    #     # We have to test weither the file comes from
    #     # a path or weither it comes from a form e.g. django
    #     is_local_file = os.path.isfile(file_to_upload.name)
    #     # No? It's a Django uploaded file
    #     if not is_local_file:
    #         item_name = file_to_upload.name
    #         contenttype = file_to_upload.content_type
    #     else:
    #         item_name = os.path.basename(file_to_upload.name)
    #         contenttype = guess_type(file_to_upload)

    #     # Create the paths
    #     items = unique_path_creator('test', item_name, rename=False)

    #     # Correct the file name if needed
    #     # and create the bucket path
    #     # Upload the file to AMAZON bucket
    #     try:
    #         self.bucket.put_object(Key=items['object_path'], Body=file_to_upload, ACL='public-read',
    #                                     ContentType=contenttype, CacheControl='max-age=24000')
    #     except boto3.exceptions.S3TransferFailedError:
    #         print('[%s]: Upload failed. %s was not uploaded.' 
    #                 % (self.__class__.__name__, items['object_path']))

access_key = 'AKIAJQZHLNUQVX7Q5QFA'
secret_key = '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'
# path='C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\scrappers\\config\\http\\tumblr_pbpegtKkNF1uokzn6o3_1280.jpg'
# path2='C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\scrappers\\config\\http\\sophie.jpg'
path3='C:\\Users\\Zadigo\\Documents\\Koding\\scrappers\\scrappers\\config\\http\\ge8h9s99m7d11.jpg'
# t=TransferManager(access_key, secret_key, 'eu-west-3', 'jobswebsite')
# # t.upload_from_local(path,'eu-west-3')
# print(t.from_local_to_existing(path2).data)
# q=QueryManager(access_key, secret_key, 'eu-west-3', 'jobswebsite')
# print(list(q.get_folder_links('test/3e7e208c6a3b27df0ca556e0f5d1207748e3f277')))
# print(q.get_file_url('test', '3e7e208c6a3b27df0ca556e0f5d1207748e3f277/sophie.jpg'))
# q.delete_file('/')


session = boto3.Session(access_key, secret_key, region_name='eu-west-3')
resource = session.resource('s3')
client = session.client('s3')

data = open(path3, 'rb')
items = {
    'Bucket': 'jobswebsite',
    'Key': 'test/3e7e208c6a3b27df0ca556e0f5d1207748e3f277/ge8h9s99m7d11.jpg',
    'Body': data.read(),
    'ACL': 'public-read',
    'ContentType': guess_type(path3)[0],
    'CacheControl': 'max-age=24000'
}
# print(client.put_object(**items))
data.close()

items = {
    'Bucket': 'jobswebsite',
    'Key': 'test/3e7e208c6a3b27df0ca556e0f5d1207748e3f277/ge8h9s99m7d11.jpg',
}

# print(client.get_object(**items))

# bucket = resource.Bucket('jobswebsite')
# print(bucket.objects)