from enum import Enum


class Message(Enum):
    info = 'info'
    warning = 'warn'
    error = 'error'


class Display:
    MESSAGE_PREFIXES = {
        Message.info: 'INFO',
        Message.warning: 'WARN',
        Message.error: 'ERR (!)'
    }

    def message(self, *parts, type=Message.info):
        prefix = Display.MESSAGE_PREFIXES.get(type, 'INFO')
        print('[ {0} ] {1}'.format(prefix, parts[0].format(*parts[1:])))

    def render(self, rendering):
        print('\n'.join(rendering))
        print('\n')
