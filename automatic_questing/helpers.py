
from logging import getLogger

from os import stat, remove, makedirs

from os.path import abspath, join, basename, isdir


def mkdir_p(path):
    temp_logger = getLogger('temp')
    try:
        if not isdir(path):
            temp_logger.info('Creating folder %s ', path)
            makedirs(path, exist_ok=True)
    except Exception as e:
        temp_logger.error('Could not create folder %s : %s ', path, e)



