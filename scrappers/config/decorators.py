import datetime
import os
from scrappers.scrappers.config.config import configuration

current_date = datetime.datetime.now().date()

def write_image(func):
    """A decorator definition that writes images to
    a default directory.
    """
    default_path = configuration.default_output_dir
    def writer(self, data, celebrity=None, *args):
        new_file_name = f'{celebrity}_{current_date.year}_{current_date.month}'
        if data:
            with open(os.path.join(default_path, new_file_name), 'wb') as f:
                print('[IMAGE]: Creating image %s' % new_file_name)
                f.write(data)
        return writer
