import argparse
import sys

# Obtained from SO because argparse calls exit() for you smh
# https://stackoverflow.com/a/5943381/4245870


class ArgumentParser(argparse.ArgumentParser):

    class Range(object):
        def __init__(self, start, end):
            self.start = start
            self.end = end

        def __eq__(self, other):
            return self.start <= other <= self.end

    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(ArgumentParser, self).error(message)
