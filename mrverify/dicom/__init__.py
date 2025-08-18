import logging
from pydicom.tag import Tag

logger = logging.getLogger(__name__)

def get_dicom_format(ds):
    tag = Tag('SOPClassUID')
    if tag in ds:
        return ds[tag].value
    return None

class MissingTagError(Exception):
    pass

