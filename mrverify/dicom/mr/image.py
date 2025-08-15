import re
import sys
import json
import logging
import warnings
from pydicom.tag import Tag
from mrverify.dicom import MissingTagError
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from nibabel.nicom import csareader

logger = logging.getLogger(__name__)

class MRImageStorage:
    def __init__(self, ds):
        self._ds = ds
        self.num_files = None

    def get(self, key, default=None):
        if hasattr(self, key):
            return getattr(self, key)
        return default

    @property
    def orientation_string(self):
        tag = Tag(0x0051, 0x100e)
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value

    @property
    def prescan_norm(self):
        if 'NORM' in self._ds.ImageType:
            return True
        return False

    @property
    def bandwidth(self):
        return float(self._ds.PixelBandwidth)
   
    @property
    def pe_direction(self):
        tag = Tag(0x0018, 0x1312) 
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value

    @property
    def flip_angle(self):
        return float(self._ds.FlipAngle)
 
    @property
    def repetition_time(self):
        return float(self._ds.RepetitionTime)

    @property
    def echo_time(self):
        return float(self._ds.EchoTime)

    @property
    def slice_thickness(self):
        return float(round(self._ds.SliceThickness, 3))

    @property
    def percent_phase_field_of_view(self):
        return float(self._ds.PercentPhaseFieldOfView)

    @property
    def base_resolution(self):
        tag = Tag(0x0018, 0x1310)
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value
       
    @property
    def pixel_spacing(self):
        return [
            round(float(x), 3) for x in self._ds.PixelSpacing
        ]

    @property
    def num_volumes(self):
        return self.num_files

    @property
    def num_slices(self):
        if 'MOSAIC' in self._ds.ImageType:
            tag = (0x0019, 0x100a)
            if tag in self._ds:
                return float(self._ds[tag].value)
            try:
                dat = self._parse_csa_ascii()
                return float(dat['sSliceArray.lSize'])
            except CSAReaderError as e:
                logger.info(f'could not retrieve number of slices from csa series header')
                logger.info(e, exc_info=True)
        return self.num_files

    @property
    def patient_position(self):
        return self._ds.PatientPosition

    @property
    def image_type(self):
        return list(self._ds.ImageType)

    @property
    def series_number(self):
        return self._ds.SeriesNumber

    @property
    def series_description(self):
        return self._ds.SeriesDescription
        
    @property
    def software_versions(self):
        try:
            dat = self._parse_csa_ascii()
            s = dat['sProtConsistencyInfo.tBaselineString']
            res = re.match(r'N4_(?P<version>.*)_LATEST.*', s)
            if res:
                return res.group('version')
        except CSAReaderError as e:
            pass
        s = self._ds.SoftwareVersions
        res = re.match(r'syngo MR (?P<version>.*)', s)
        version = res.group('version')
        if version == 'E11':
            return 'VE11'
        return version

    @property
    def manufacturer(self):
        return self._ds.Manufacturer

    @property
    def manufacturer_model_name(self):
        return self._ds.ManufacturerModelName

    @property
    def dicom_format(self):
        tag = (0x0008, 0x0016)
        if tag in self._ds:
            return self._ds[tag].value
        return None

    @property
    def secondary_image_type(self):
        try:
            item = self._ds[(0x5200,0x9230)][0]
            item = item[(0x0021,0x11fe)][0]
            item = item[(0x0021,0x1175)]
        except KeyError:
            return None
        return list(item.value)

    @property
    def software_version(self):
        tag = (0x0018, 0x1020)
        if tag in self._ds:
            return self._ds[tag].value
        return None
    
    def _guess_coil(self):
        # try guessing from coil elements
        logger.info('attempting to guess coil from coil elements')
        match self.coil_elements:
            case 'HEA':
                coil = 'Head_32'
            case 'HEP':
                return 'Head_32'
            case 'HEA;HEP':
                return 'Head_32'
            case 'HC1-7;NC1,2':
                return 'HeadNeck_64'
            case _:
                logger.warning(f'could not determine head coil from '
                    f'coil elements {self.coil_elements}')

        # try counting channels in CSA image header "UsedChannelString"
        logger.info('attempting to guess coil from CSA image header UsedChannelString')
        try:
            dat = self._csa_header_info('image')
            channels = dat['tags']['UsedChannelString']['items'][0]
            num_channels = len(channels)
            match num_channels:
                case 32:
                    return 'Head_32'
                case 64:
                    return 'HeadNeck_64'
                case _:
                    logger.warning('could not determine coil from the number '
                        f'of channels {num_channels}')
        except CSAReaderError as e:
            logger.info(f'could not retrieve coil from csa series header')
            logger.info(e, exc_info=True)
        except Exception as e:
            logger.info(f'unexpected error reading coil from csa series header')
            logger.info(e, exc_info=True)

        return 'Unknown'

    @property
    def coil_elements(self):
        tag = (0x0051,0x100f)
        if tag not in self._ds:
            dat = self._parse_csa_ascii()
            return dat['sCoilSelectMeas.sCoilStringForConversion']
        return self._ds[tag].value

    @property
    def coil(self):
        try:
            dat = self._parse_csa_ascii()
            return dat['sCoilSelectMeas.aRxCoilSelectData[0].asList[0].sCoilElementID.tCoilID']
        except CSAReaderError as e:
            logger.info(f'could not retrieve coil from csa series header')
            logger.info(e, exc_info=True)
        except Exception as e:
            logger.info(f'unexpected error reading coil from csa series header')
            logger.info(e, exc_info=True)

        try:
            return self._guess_coil() 
        except CSAReaderError as e:
            logger.info(f'could not retrieve coil from csa series header')
            logger.info(e, exc_info=True)
        except Exception as e:
            logger.info(f'unexpected error reading coil from csa series header')
            logger.info(e, exc_info=True)

        return None

    @property
    def abs_table_position(self):
        try:
            data = self._csa_header_info('image')
            return data['tags']['ImaAbsTablePosition']['items'][2]
        except CSAReaderError as e:
            logger.debug(f'could not retrieve table position from csa header')
            logger.debug(e, exc_info=True)
        except Exception as e:
            logger.info(f'unexpected error reading table position from csa header')
            logger.info(e, exc_info=True)

    def _csa_header_info(self, csa_type='image'):
        match csa_type:
            case 'image':
                tag = Tag(0x0029, 0x1010)
            case 'series':
                tag = Tag(0x0029, 0x1020)
            case _:
                raise Exception(f'csa type not supported {csa_type}')
        if tag not in self._ds:
            raise MissingSiemensCSAHeader(tag)
        try:
            result = csareader.read(self._ds[tag].value)
        except Exception as e:
            raise CSAReaderError(e) from e
        return result

    def _parse_csa_ascii(self):
        dat = dict()
        tag = Tag(0x0029, 0x1020)
        if tag not in self._ds:
            raise MissingSiemensCSAHeader(tag)
        value = self._ds[tag].value
        value = value.decode(errors='ignore')
        match = re.search(r'### ASCCONV BEGIN.*?###(.*)### ASCCONV END ###', value, re.DOTALL)
        if not match:
            raise Exception('could not find ASCCONV section in Siemens CSA header')
        ascconv = match.group(1).strip()
        for line in ascconv.split('\n'):
            match = re.match(r'(.*?)\s+=\s+(.*)', line)
            key,value = match.groups()
            dat[key] = value.strip('"')
        return dat

class CSAReaderError(Exception):
    pass

class MissingSiemensCSAHeader(CSAReaderError):
    pass


