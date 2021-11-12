import logging
from mrverify.scanner.siemens import Siemens

logger = logging.getLogger(__name__)

class Prisma(Siemens):
    def __init__(self, config):
        super().__init__(config['Siemens']['Prisma'])
            
    @classmethod
    def check_model(cls, model):
        if model in ['Prisma', 'Prisma_fit']:
            return True
        return False
