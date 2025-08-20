from . import gmail
from . import smtp

class NotifierCreator:
    @staticmethod
    def create(conf):
        handler = conf.query('$.Notifications.handler.type')
        match handler.lower():
            case 'gmail':
                return gmail.Notifier(conf)
            case 'smtp':
                return smtp.Notifier(conf)
            case _:
                raise Exception(f'unexpected notification handler {handler}')

