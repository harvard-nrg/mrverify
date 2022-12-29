import os
import io
import csv
import json
import logging
from natsort import natsorted
from collections import namedtuple
from jinja2 import Template

__dir__ = os.path.dirname(__file__)

logger = logging.getLogger(__name__)

class Report:
    def __init__(self):
        self.data = dict()
        self.meta = dict()
        self.has_errors = False
        template = os.path.join(__dir__, "template.html")
        with open(template) as fo:
            self.template = Template(fo.read())

    def add(self, scan, checker):
        self.has_errors = self.has_errors or checker.has_errors
        self.data[scan['id']] = {
            'scan': scan,
            'checker': checker
        }

    def add_meta(self, meta):
        self.meta = meta

    def generate_html(self, saveto='report.html'):
        self.data = dict(natsorted(self.data.items()))
        dirname = os.path.dirname(saveto)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(saveto, 'w') as fo:
            fo.write(self.template.render(
                data=self.data,
                meta=self.meta,
                errors=self.has_errors
            ))

class Result(object):
    def __init__(self, name, actual, expected):
        self.name = name
        self.actual = actual
        self.expected = expected

class Ok(Result):
    def __str__(self):
        return 'Ok'

class Err(Result):
    def __str__(self):
        return 'Err'

class Miss(Result):
    def __str__(self):
        return 'Miss'

