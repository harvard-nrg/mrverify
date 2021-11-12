import logging
from mrverify.scanner.siemens import Siemens

logger = logging.getLogger(__name__)

class Skyra(Siemens):
    def __init__(self, config):
        super().__init__(config['Siemens']['Skyra'])

    @classmethod
    def check_model(cls, model):
        if model in ['Skyra']:
            return True
        return False
 
