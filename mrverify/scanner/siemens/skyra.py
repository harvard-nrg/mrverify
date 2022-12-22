import logging
from mrverify.scanner.siemens import Siemens

logger = logging.getLogger(__name__)

class Skyra(Siemens):
    def __init__(self, conf):
        skyra = conf.query('$.Siemens.Skyra')
        super().__init__(skyra)

    @classmethod
    def check_model(cls, model):
        if model in ['Skyra']:
            return True
        return False
 
