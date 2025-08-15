from .image import MRImageStorage
from .enhanced import EnhancedMRImageStorage
from .. import get_dicom_format

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
                raise Exception(f'unhandled dicom format {self._dicom_format}, {self._dicom_format.name}')

