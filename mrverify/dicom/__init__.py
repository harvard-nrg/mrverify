import os
import re
import pydicom
import logging
from mrverify.report import Ok, Err, Miss
from pydicom.errors import InvalidDicomError
from pydicom.filereader import read_preamble

logger = logging.getLogger(__name__)

def get_dicom_format(ds):
    tag = (0x0008, 0x0016)
    if tag in ds:
        return ds[tag].value
    return None

class MissingTagError(Exception):
    pass

