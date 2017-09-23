# -*- coding: utf-8 -*-
import inspect

from mousey import commands


class HelpFormatter(commands.HelpFormatter):
    def get_ending_note(self):
        note = f"""
        Type "{self.clean_prefix}{self.context.invoked_with} <command>" for more information on a command.
        If you need more detailed information refer to the documentation at https://frostluma.github.io/Mousey/.
        """
        return inspect.cleandoc(note)
