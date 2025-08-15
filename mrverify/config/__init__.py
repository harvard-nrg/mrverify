import os
import sys
import yaml
import logging
from pathlib import Path
from urllib.parse import urlparse
from jsonpath_ng import jsonpath, parse

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, filename, cache_dir='~/.cache/mrverify'):
        self._filename = filename
        self._cache_dir = cache_dir
        self._content = self.parse_file()

    @staticmethod
    def load(confd, scanner):
        path = Path(
            confd,
            scanner.manufacturer,
            scanner.model,
            scanner.software,
            scanner.coil,
            'mrverify.yaml'
        )
        logger.info(f'loading {path}')
        return Config(path)

    def parse_file(self):
        with open(self._filename) as fo:
            config = yaml.load(fo, Loader=yaml.FullLoader)
        return config['mrverify']

    def query(self, expression, **kwargs):
        exp = parse(expression)
        matches = exp.find(self._content)
        num_matches = len(matches)
        if num_matches == 0:
            if 'default' in kwargs:
                return kwargs['default']
            raise ConfigQueryError(f'no result returned from JSONPath {expression}')
        elif num_matches == 1:
            return matches[0].value
        else:
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
