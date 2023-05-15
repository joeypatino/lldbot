import inspect
import optparse
import shlex
import sys

from command_parser import Subcommand, SubcommandsOptionParser
from configure_command import ConfigureCommand
from explain_command import ExplainCommand


class LLDBotCommand:
    program = 'lldbot'

    @classmethod
    def register_lldb_command(cls, debugger, module_name):
        parser = cls.create_options()
        cls.__doc__ = parser.format_help()
        # Add any commands contained in this module to LLDB
        command = 'command script add -o -c %s.%s %s' % (module_name,
                                                         cls.__name__,
                                                         cls.program)
        debugger.HandleCommand(command)
        print('The "{0}" command has been installed, type "help {0}" or "{0} '
              '--help" for detailed help.'.format(cls.program))

    @classmethod
    def create_options(cls):
        # explain subcommand
        explain_cmd = Subcommand('explain',
                                 optparse.OptionParser(usage='%prog [OPTIONS] [ARGS...]'),
                                 help='analyse crash information and prints cause and solution')

        explain_cmd.parser.add_option(
            '--api_key',
            action='store',
            dest='api_key',
            help='api_key = None',
            default='')

        explain_cmd.parser.add_option(
            '--in-scope',
            action='store',
            dest='inscope',
            help='in_scope_only = True',
            default=True)

        explain_cmd.parser.add_option(
            '--arguments',
            action='store',
            dest='arguments',
            help='arguments = True',
            default=True)

        explain_cmd.parser.add_option(
            '--locals',
            action='store',
            dest='locals',
            help='locals = True',
            default=True)

        explain_cmd.parser.add_option(
            '--statics',
            action='store',
            dest='statics',
            help='statics = True',
            default=True)

        config_cmd = Subcommand('configure',
                                optparse.OptionParser(usage='%prog [OPTIONS] [ARGS...]'),
                                help='configures the openai api key to be used')

        config_cmd.parser.add_option(
            '--api_key',
            action='store',
            dest='api_key',
            help='api_key = None',
            default='')

        # Set up the global parser and its options.
        parser = SubcommandsOptionParser(
            subcommands=(explain_cmd, config_cmd)
        )

        return parser

    def __init__(self, debugger, unused):
        self.parser = self.create_options()

    def __call__(self, debugger, command, exe_ctx, result):
        # Use the Shell Lexer to properly parse up command options just like a
        # shell would
        command_args = shlex.split(command)

        try:
            # Parse the global options and the subcommand options.
            options, subcommand, suboptions, subargs = self.parser.parse_args(command_args)
            # (options, args) = self.parser.parse_args(command_args)
        except:
            # if you don't handle exceptions, passing an incorrect argument to
            # the OptionParser will cause LLDB to exit (courtesy of OptParse
            # dealing with argument errors by throwing SystemExit)
            print('')
            result.SetError("option parsing failed")
            return

        if subcommand.name == 'explain':
            try:
                ExplainCommand(suboptions, debugger, exe_ctx, result)
            except:
                result.SetError("Failed to explain")

        if subcommand.name == 'configure':
            try:
                ConfigureCommand(suboptions.api_key)
            except:
                result.SetError("Failed to configure")


def __lldb_init_module(debugger, dict):
    # Register all classes that have a register_lldb_command method
    for _name, cls in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(cls) and callable(getattr(cls,
                                                     "register_lldb_command",
                                                     None)):
            cls.register_lldb_command(debugger, __name__)
