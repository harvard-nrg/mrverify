import os
import yaml
import logging
from urllib.parse import urlparse
from jsonpath_ng import jsonpath, parse

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, filename, hostname, default_cache_dir='~/.cache/mrverify'):
        self._filename = filename
        self._hostname = hostname
        self._default_cache_dir = default_cache_dir
        self._content = self.parse_file()
        self.config_dir = os.path.dirname(filename)
        self.cache_dir = self.get_cache_dir()

    def parse_file(self):
        logger.info(f'parsing {self._filename}')
        with open(self._filename) as fo:
            return yaml.load(fo, Loader=yaml.FullLoader)

    def query(self, expression, **kwargs):
        exp = parse(expression)
        matches = exp.find(self._content)
        match len(matches):
            case 0:
                if 'default' in kwargs:
                    return kwargs['default']
                raise ConfigQueryError(f'no result returned from JSONPath {expression}')
            case 1:
                return matches[0].value
            case _:
                raise ConfigError(f'multiple results returned from JSONPath {expression}')

    def get_cache_dir(self):
        cache_dir = self._default_cache_dir
        try:
            cache_dir = self.query('$.Storage.cache_dir')
        except ConfigQueryError as e:
            logger.debug(e)
            pass
        cache_dir = os.path.join(cache_dir, self._hostname)
        cache_dir = os.path.expanduser(cache_dir)
        return cache_dir

class ConfigQueryError(Exception):
    pass
