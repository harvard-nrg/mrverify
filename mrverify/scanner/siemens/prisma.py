import logging
from mrverify.scanner.siemens import Siemens

logger = logging.getLogger(__name__)

class Prisma(Siemens):
    def __init__(self, conf):
        prisma = conf.query('$.Siemens.Prisma')
        super().__init__(prisma)
            
    @classmethod
    def check_model(cls, model):
        if model in ['Prisma', 'Prisma_fit']:
            return True
        return False
