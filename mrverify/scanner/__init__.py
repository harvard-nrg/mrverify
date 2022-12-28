import os
import re
import pydicom
import logging
from mrverify.report import Ok, Err, Miss
from pydicom.errors import InvalidDicomError
from pydicom.filereader import read_preamble

logger = logging.getLogger(__name__)

class BaseScanner(object):
    def __init__(self, config):
        self._config = config
        self._params = dict()
        self.result = dict()
        self.has_errors = False

    def needs_checking(self, scan):
        for item in self._config:
            match = True
            for key,value in iter(item['scan'].items()):
                val = scan.get(key, '')
                # collapse consecutive backslash chars in image type
                if key == 'image_type':
                    value = re.sub(r'\\+', r'\\', value)
                    val = re.sub(r'\\+', r'\\', val)
                strcmp = val.casefold() == value.casefold()
                match = match and strcmp
            if match:
                self._params = item['params']
                return True
        return False

    def check_dir(self, folder):
        files = self.get_dicoms(folder)
        num_files = len(files)
        for f in files:
            fullfile = os.path.join(folder, f)
            self.check_file(fullfile, num_files)

    def get_dicoms(self, folder):
      files = list()
      for f in os.listdir(folder):
        fullfile = os.path.join(folder, f)
        with open(fullfile, 'rb') as fo:
          try:
            read_preamble(fo, force=False)
          except InvalidDicomError as e:
            continue
        files.append(f)
      return files

    def check_file(self, f, num_files):
        logger.debug(f'checking file {os.path.basename(f)}')
        try:
          ds = pydicom.read_file(f)
        except InvalidDicomError as e:
          return
        ds.num_files = num_files
        for param,expected in iter(self._params.items()):
            # skip checking this parameter if any previous file was not Ok
            res = self.result.get(param, None)
            if res and not isinstance(res, Ok):
                continue
            # check if this is a regex
            regex = re.match('regex\((.*)\)', str(expected))
            if regex:
              expected = regex.group(1).strip()
            getter = getattr(self, param)
            try:
                actual = getter(ds)
            except MissingTagError as e:
                logger.debug(f'missing {param} tag {e.tagstr}')
                self.result[param] = Miss(param, '[MISSING TAG]', expected)
                continue
            logger.debug(f'{param} assert actual={actual} == expected={expected}')
            try:
                if regex:
                    assert re.match(expected, actual) != None
                else:
                    assert actual == expected
            except AssertionError as e:
                logger.debug(f'{param} assertion error actual={actual} != expected={expected}')
                self.result[param] = Err(param, actual, expected)
                self.has_errors = True
                continue
            self.result[param] = Ok(param, actual, expected)

class MissingTagError(Exception):
    def __init__(self, tag):
        self.tag = tag
        self.message = tag
        self.tagstr = f'(0x{self.tag[0]:04x},0x{self.tag[1]:04x})'

