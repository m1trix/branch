import argparse


class Option:
    def __init__(self, name, letter, help):
        self._name = name
        self._letter = letter
        self._has_value = True
        self._help = help

    @property
    def help(self):
        return self._help

    @property
    def letter(self):
        return self._letter

    @property
    def name(self):
        return self._name

    @property
    def has_value(self):
        return self._has_value


class FlagOption(Option):
    def __init__(self, name, letter, help):
        Option.__init__(self, name, letter, help)
        self._has_value = False


class Command:
    def __init__(self, name, help, options=[]):
        self._name = name
        self._help = help
        self._options = options

    @property
    def help(self):
        return self._help

    @property
    def name(self):
        return self._name

    @property
    def options(self):
        return self._options


class Controller:
    def select(self, commands):
        commands = {command.name: command for command in commands}
        parser = self._create_root_parser(commands)
        subparsers = parser.add_subparsers(dest='__command__')
        for command in commands.values():
            self._add_command_parser(subparsers, command)
        args = vars(parser.parse_args())

        command = commands[args['__command__']]
        return command.name, {
            option.name: args.get(option.name)
            for option
            in command.options
        }

    def _create_root_parser(self, commands):
        root_command = commands.get(None)
        args = {
            'allow_abbrev': False,
            'description': ''
        }
        if root_command is not None:
            args['description'] = commands[None].help
        parser = argparse.ArgumentParser(**args)
        if root_command is not None:
            for option in root_command.options:
                self._add_option_parser(parser, option)
        return parser

    def _add_command_parser(self, subparsers, command):
        if command.name is None:
            return

        subparser = subparsers.add_parser(command.name, help=command.help)
        for option in command.options:
            self._add_option_parser(subparser, option)

    def _add_option_parser(self, parser, option):
        flags = ['-' + option.letter, '--' + option.name]
        args = {
            'help': option.help,
            'action': {
                True: 'store_const',
                False: 'store_true'
            }[option.has_value]
        }
        parser.add_argument(*flags, **args)
