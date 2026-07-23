import logging
from .image import MRImageStorage
from .enhanced import EnhancedMRImageStorage
from .. import get_dicom_format

logger = logging.getLogger(__name__)

class ImageCreator:
    def __init__(self, ds):
        self._ds = ds
        self._dicom_format = get_dicom_format(ds)

    def create(self):
        match self._dicom_format.name:
            case 'MR Image Storage':
                return MRImageStorage(self._ds)
            case 'Enhanced MR Image Storage':
                return EnhancedMRImageStorage(self._ds)
            case 'Enhanced SR Storage':
                return EnhancedMRImageStorage(self._ds) 
            case _:
                logger.warning(
                    f'unhandled dicom format {self._dicom_format}, '
                    f'{self._dicom_format.name}, treating as MRImageStorage'
                )
                return MRImageStorage(self._ds)

