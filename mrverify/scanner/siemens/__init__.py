import os
import re
import logging
from mrverify.scanner import BaseScanner, MissingTagError

logger = logging.getLogger(__name__)

class Siemens(BaseScanner):
    def csa(self, ds):
        dat = dict()
        tag = (0x0029,0x1020)
        if tag not in ds:
          raise MissingTagError(tag)
        value = ds[tag].value
        value = value.decode(errors='ignore')
        match = re.search('### ASCCONV BEGIN.*?###(.*)### ASCCONV END ###', value, re.DOTALL)
        if not match:
          raise Exception('could not find ASCCONV section in Siemens CSA header')
        ascconv = match.group(1).strip()
        for line in ascconv.split('\n'):
            match = re.match('(.*?)\s+=\s+(.*)', line)
            key,value = match.groups()
            dat[key] = value.strip('"')
        return dat

    def image_orientation_patient(self, ds):
        return ds.ImageOrientationPatient

    def pixel_spacing(self, ds):
        return [round(float(x), 3) for x in ds.PixelSpacing]

    def shim_current(self, ds):
        raise MissingTagError((0x0000, 0x0000))
        
    def orientation_string(self, ds):
        tag = (0x0051,0x100e)
        if tag not in ds:
            raise MissingTagError(tag)
        return ds[tag].value 

    def bandwidth(self, ds):
        return float(ds.PixelBandwidth)

    def prescan_norm(self, ds):
        if 'NORM' in ds.ImageType:
            return True
        return False

    def base_resolution(self, ds):
        tag = (0x0018,0x1310)
        if tag not in ds:
            raise MissingTagError(tag)
        return ds[tag].value

    def pe_direction(self, ds):
        tag = (0x0018,0x1312) 
        if tag not in ds:
            raise MissingTagError(tag)
        return ds[tag].value

    def flip_angle(self, ds):
        return float(ds.FlipAngle)

    def coil_elements(self, ds):
        tag = (0x0051,0x100f)
        if tag not in ds:
            dat = self.csa(ds)
            return dat['sCoilSelectMeas.sCoilStringForConversion']
        return ds[tag].value
        
    def repetition_time(self, ds):
        return float(ds.RepetitionTime)

    def echo_time(self, ds):
        return float(ds.EchoTime)

    def slice_thickness(self, ds):
        return float(round(ds.SliceThickness, 3))

    def percent_phase_field_of_view(self, ds):
        return float(ds.PercentPhaseFieldOfView)

    def patient_position(self, ds):
        return ds.PatientPosition

    def num_slices(self, ds):
        if 'MOSAIC' in ds.ImageType:
          tag = (0x0019, 0x100a)
          if tag not in ds:
            dat = self.csa(ds)
            return float(dat['sSliceArray.lSize'])
          return float(ds[tag].value)
        return ds.num_files

    def num_volumes(self, ds):
        return ds.num_files

    def fov_read(self, ds):
        tag = (0x0051,0x100c)
        if tag not in ds:
            raise MissingTagError(tag)
        value = ds[tag].value
        match = re.match('^FoV \d+\*(\d+)$', value)
        return int(match.group(1))

