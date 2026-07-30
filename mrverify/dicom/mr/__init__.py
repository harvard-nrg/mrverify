from .image import MRImageStorage
from .enhanced import EnhancedMRImageStorage
from .. import get_dicom_format

class ImageCreator:
    def __init__(self, ds):
        self._ds = ds
        self.dicom_format = get_dicom_format(ds)

    def create(self):
        match self.dicom_format.name:
            case 'MR Image Storage':
                return MRImageStorage(self._ds)
            case 'Enhanced MR Image Storage':
                return EnhancedMRImageStorage(self._ds)
            case 'Enhanced SR Storage':
                return EnhancedMRImageStorage(self._ds) 
            case _:
                raise Exception(f'unhandled dicom format {self.dicom_format}, {self.dicom_format.name}')

