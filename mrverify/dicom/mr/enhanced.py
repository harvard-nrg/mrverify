import sys
import logging
from pydicom.tag import Tag
from mrverify.dicom import MissingTagError
from .image import MRImageStorage

logger = logging.getLogger(__name__)

class EnhancedMRImageStorage(MRImageStorage):
    def __init__(self, ds):
        super().__init__(ds)

    @property
    def prescan_norm(self):
        if 'NORM' in self.secondary_image_type:
            return True
        return False

    @property
    def base_resolution(self):
        return [
            0.0,
            self._ds.Rows,
            self._ds.Columns,
            0.0
        ] 

    @property
    def num_slices(self):
        return self.num_frames

    @property
    def num_frames(self):
        tag = Tag('NumberOfFrames')
        if tag not in self._ds:
            raise MissingTagError(tag)
        return self._ds[tag].value

    @property
    def percent_phase_field_of_view(self):
        item = self._ds.SharedFunctionalGroupsSequence[0]
        item = item.MRFOVGeometrySequence[0]
        return item.PercentPhaseFieldOfView

    @property
    def pe_direction(self):
        item = self._ds.SharedFunctionalGroupsSequence[0]
        item = item.MRFOVGeometrySequence[0]
        return item.InPlanePhaseEncodingDirection

    @property
    def bandwidth(self):
        item = self._ds.SharedFunctionalGroupsSequence[0]
        item = item.MRImagingModifierSequence[0]
        return item.PixelBandwidth

    @property
    def flip_angle(self):
        item = self._ds.SharedFunctionalGroupsSequence[0]
        item = item.MRTimingAndRelatedParametersSequence[0]
        return item.FlipAngle

    @property
    def repetition_time(self):
        item = self._ds.SharedFunctionalGroupsSequence[0]
        item = item.MRTimingAndRelatedParametersSequence[0]
        return item.RepetitionTime

    @property
    def coil(self):
        item = self._ds.SharedFunctionalGroupsSequence[0]
        item = item.MRReceiveCoilSequence[0]
        return item.ReceiveCoilName

    @property
    def echo_time(self):
        item = self._ds.PerFrameFunctionalGroupsSequence[0]
        item = item.MREchoSequence[0]
        return round(item.EffectiveEchoTime, 3)

    @property
    def orientation_string(self):
        raise MissingTagError()

    @property
    def pixel_spacing(self):
        item = self._ds.PerFrameFunctionalGroupsSequence[0]
        item = item.PixelMeasuresSequence[0]
        return item.PixelSpacing

    @property
    def slice_thickness(self):
        item = self._ds.PerFrameFunctionalGroupsSequence[0]
        item = item.PixelMeasuresSequence[0]
        return item.SliceThickness

    @property
    def coil_elements(self):
        item = self._ds.PerFrameFunctionalGroupsSequence[0]
        item = item[(0x0021, 0x11fe)][0]
        return item[(0x0021, 0x114f)].value

    @property
    def abs_table_position(self):
        item = self._ds.PerFrameFunctionalGroupsSequence[0]
        item = item[(0x0021, 0x11fe)][0]
        item = item[(0x0021, 0x1145)]
        return list(item.value)[-1]
