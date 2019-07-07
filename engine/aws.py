import boto3
from boto3.s3.transfer import S3Transfer
import os
from mimetypes import guess_type, guess_extension
import secrets

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
    object's new name, path and url
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
    object_url = create_object_url(object_path)
    
    return {'object_name': [name, guess_type(filename)], 'object_path': object_path, 
                'object_url': object_url, 'unique_entry': unique_entry}


class AWS:
    """This is the base used to connect to an AWS bucket.

    Parameters
    ----------

        file_to_post
        
        access_key
        
        secret_key
        
        service_name
        
        region: The region of your bucket
        
        bucket: Your bucket's name
    """
    def __init__(self, access_key, secret_key, region, bucket):
        session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        client = session.resource(bucket, region_name=region)
        self.bucket = client.Bucket(bucket)

class QueryManager(AWS):
    def get_all(self):
        return [item for item in self.bucket.objects.all()]

    def get_folder(self, folder, choices=False):
        """Get the specific items of a folder
        """
        obj = tuple((item.key, 'item') for item in self.bucket.objects.filter(Prefix=folder))
        return obj

    # def get_folder_links(self, folder):
    #     """Get the specific items' links in a folder
    #     """
    #     objs = self.get_aws_folder(folder)
    #     for obj in objs:
    #          yield aws_base_url(obj=obj[0])

    # def get_file_url(self):
    #     # region = eu-west-3
    #     # https://s3.eu-west-3.amazonaws.com/jobswebsite/banners/rachel-williams-310248-unsplash.jpg
    #     # uri = 'https://s3.{region}.amazonaws.com/{bucket}/{folder}/{file}'
    #     item = self.bucket.objects.filter(Prefix='banners', Delimiter='/', Key='rawpixel-744338-unsplash.jpg')
    #     print(item.key)
    #     # return uri.format(region=region, bucket=bucket, folder=folder, file=file)

class TransferManager(AWS):
    def upload(self, file_to_upload, bucket, model=None, request=None):
        # We have to test weither the file comes from
        # a path or weither it comes from a form e.g. django
        is_local_file = os.path.isfile(file_to_upload.name)
        # No? It's a Django uploaded file
        if not is_local_file:
            item = file_to_upload.name
            contenttype = file_to_upload.content_type
        else:
            item = os.path.basename(file_to_upload.name)
            contenttype = guess_type(file_to_upload)

        # Create the paths
        items = unique_path_creator('test', item)

        # Correct the file name if needed
        # and create the bucket path
        # Upload the file to AMAZON bucket
        try:
            self.bucket.put_object(Key=items['object_path'], Body=file_to_upload, ACL='public-read',
                                        ContentType=file_to_upload.content_type, CacheControl='max-age=24000')
        except boto3.exceptions.S3TransferFailedError:
            print('[%s]: Upload failed. %s was not uploaded.' 
                    % (self.__class__.__name__, items['object_path']))


# with open('C:\\Users\\Zadigo\\Documents\\WTA_Data\\eugenie_bouchard_2019_6_17a9d5be3a.json', 'rb') as f:
#     print(f.content_type)

# print(unique_path_creator('test', 'test.png'))