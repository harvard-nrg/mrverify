import re
import logging
from mrverify.dicom import MissingTagError
from mrverify.report import Ok, Err, Miss

logger = logging.getLogger(__name__)

class Validator:
    def __init__(self):
        self.result = dict()
        self.has_errors = False

    def validate(self, scan, params):
        for param,expected in iter(params.items()):
            try:
                actual = scan.get(param)
            except MissingTagError as e:
                self.result[param] = Miss(param, '[MISSING TAG]', expected)
                continue

            # find correct validator type
            validator = None
            for VType in [Regex, Range, Scalar]:
                validator = VType.parse(expected)
                if validator:
                    break

            # run validator assertion
            try:
                validator.assertion(actual)
            except AssertionError as e:
                logger.debug(f'{param} assertion error actual={actual} != expected={expected}')
                self.result[param] = Err(param, actual, expected)
                self.has_errors = True
                continue

            # parameter is ok
            self.result[param] = Ok(param, actual, expected)

class Scalar:
    def __init__(self, expected):
        self.expected = expected

    @staticmethod
    def parse(s):
        return Scalar(s)

    def assertion(self, actual):
        assert actual == self.expected
     
class Regex:
    def __init__(self, expression):
        self.expression = expression

    @staticmethod
    def parse(s):
        expr = r'regex\((?P<expr>.*)\)'
        match = re.match(expr, str(s))
        if match:
            return Regex(match.group('expr'))

    def assertion(self, actual):
        assert re.match(self.expression, actual) != None    

class Range:
    def __init__(self, min, max):
        self.min = float(min)
        self.max = float(max)

    @staticmethod
    def parse(s):
        match = re.match(r'range\((?P<min>.*),(?P<max>.*)\)', str(s))
        if match:
            min = match.group('min')
            max = match.group('max')
            return Range(float(min), float(max))
   
    def assertion(self, actual):
        logger.debug(f'asserting {self.min} <= {actual} <= {self.max}')
        assert self.min <= float(actual) <= self.max

