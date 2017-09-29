# -*- coding: utf-8 -*-
import inspect
from typing import Generator

import discord
from discord.ext import commands
from discord.ext.commands.view import quoted_word, StringView

from .context import Context
from .errors import CommandError, BadArgument, InsufficientPermissions, MissingRequiredArgument


__all__ = (
    'bot_has_permissions',
    'check',
    'Command',
    'command',
    'Group',
    'group',
    'GroupMixin',
    'guild_only',
    'has_permissions',
    'is_nsfw',
    'is_owner',
    'quoted_word',
    'RecalledArgument',
    'schedule',
    'StringView',
    'ViewConverter',
)

# reassignment to have fewer imports in the actual bot code
check = commands.check
guild_only = commands.guild_only
is_nsfw = commands.is_nsfw
is_owner = commands.is_owner


# todo: permissions decorator


class RecalledArgument:
    """
    Converters may return parts of the given argument to be re-used on the next parameter the command has.

    This allows for having multi word arguments in the middle of commands: command <multi word> <rest>
    As well as having optional arguments in between required ones: command <argument=default> <required>
    """

    def __init__(self, argument: str):
        self.argument = argument


class ViewConverter:
    """
    Converters inheriting from this class do not get the argument passed as a string, but rather the StringView.

    This makes it convenient to write multi word converters, as the words method allows getting one quoted
    word from the view at a time.
    """

    @staticmethod
    def words(view: StringView) -> Generator[str, None, None]:
        """Yields each argument from a given StringView."""
        while not view.eof:
            view.skip_ws()
            yield quoted_word(view)


class Command(commands.Command):
    """
    Command subclass to allow lower level access to command parsing and a few other utilities.
    To see how to properly utilise these changes see mousey/ext/internal/testing.py

    Parameters
    ----------
    typing : bool
        Whether the bot should type in the current channel while executing this command. Defaults to False.
    """

    def __init__(self, *, typing: bool=False, **kwargs):
        super().__init__(**kwargs)

        self.typing = typing

    async def transform(self, ctx: Context, param):
        required = param.default is param.empty
        converter = self._get_converter(param)
        consume_rest_is_special = param.kind == param.KEYWORD_ONLY and not self.rest_is_raw

        view = ctx.view
        view.skip_ws()

        if view.eof:
            if param.kind == param.VAR_POSITIONAL:
                raise RuntimeError()  # break the loop
            if required:
                raise MissingRequiredArgument(param)
            return param.default

        if inspect.isclass(converter) and issubclass(converter, ViewConverter):
            argument = view
        elif consume_rest_is_special:
            argument = view.read_rest().strip()
        else:
            argument = quoted_word(view)

        try:
            result = await self.do_conversion(ctx, converter, argument)
        except CommandError as e:
            raise e
        except Exception as e:
            try:
                name = converter.__name__
            except AttributeError:
                name = converter.__class__.__name__

            raise BadArgument(f'Converting to "{name}" failed for parameter "{param.name}".') from e

        if not result or isinstance(result, RecalledArgument):
            if required:
                raise MissingRequiredArgument(param)

            if isinstance(result, RecalledArgument):
                view.index -= len(result.argument)
            result = param.default

        elif isinstance(result, tuple) and isinstance(result[-1], RecalledArgument):
            *result, recalled = result
            view.index -= len(recalled.argument)

            if len(result) == 1:
                result = result[0]

        return result

    async def _parse_arguments(self, ctx: Context):
        ctx.args = args = [ctx] if self.instance is None else [self.instance, ctx]
        ctx.kwargs = kwargs = {}

        view = ctx.view
        iterator = iter(self.params.items())

        if self.instance is not None:
            # we have 'self' as the first parameter so just advance
            # the iterator and resume parsing
            try:
                next(iterator)
            except StopIteration:
                raise discord.ClientException(f'Callback for {self.name} command is missing "self" parameter.')

        # next we have the 'ctx' as the next parameter
        try:
            next(iterator)
        except StopIteration:
            raise discord.ClientException(f'Callback for {self.name} command is missing "ctx" parameter.')

        for name, param in iterator:
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                transformed = await self.transform(ctx, param)
                args.append(transformed)

            elif param.kind == param.KEYWORD_ONLY:
                # kwarg only param denotes "consume rest" semantics
                if self.rest_is_raw:
                    converter = self._get_converter(param)
                    argument = view.read_rest()
                    kwargs[name] = await self.do_conversion(ctx, converter, argument)
                    break

                kwargs[name] = await self.transform(ctx, param)

            elif param.kind == param.VAR_POSITIONAL:
                while not view.eof:
                    try:
                        transformed = await self.transform(ctx, param)
                        args.append(transformed)
                    except RuntimeError:
                        break

        if not self.ignore_extra:
            if not view.eof:
                raise commands.TooManyArguments(f'Too many arguments passed to {self.qualified_name}')

    async def invoke(self, ctx: Context):
        # this is basically copied from the superclass
        # the actual_invoke func is there to not type during preparation (verifying checks etc)
        await self.prepare(ctx)

        async def actual_invoke():
            ctx.invoked_subcommand = None
            injected = commands.core.hooked_wrapped_callback(self, ctx, self.callback)
            await injected(*ctx.args, **ctx.kwargs)

        if self.typing:
            async with ctx.typing():
                return await actual_invoke()
        await actual_invoke()


class GroupMixin(commands.GroupMixin):
    # shortcut decorators to add commands and groups to the internal commands list
    # these are just copied from the superclass to use the new Command class
    def command(self, *args, **kwargs):
        def decorator(func):
            cmd = command(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        def decorator(func):
            cmd = group(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator


class Group(GroupMixin, commands.Group, Command):
    pass


def command(name: str=None, cls=Command, **attrs):
    return commands.command(name, cls, **attrs)


def group(name: str=None, invoke_without_command: bool=True, **attrs):
    return command(name, cls=Group, invoke_without_command=invoke_without_command, **attrs)


def schedule(interval,  wait_until_ready=True):
    """
    Schedule a method to be called later, on a specified interval.

    .. note:: The interval is also the initial sleep, the method will not get called immediately after startup

    Parameters
    ----------
    interval : int
        Seconds to wait between calling the method
    wait_until_ready : bool
        Whether to wait until the bot has logged in before running for the first time, defaults to True
    """
    def decorator(func):
        func.__schedule = {'interval': interval, 'wait_until_ready': wait_until_ready}
        return func

    return decorator


def has_permissions(*, check_bot=True, **perms):
    """
    Decorator to add a permission check to a command. This checks the bots and the users permissions.

    The permissions must match the names of the discord.Permissions attributes,
    as falsy values are returned for unresolved permissions.

    Parameters
    ----------
    check_bot : bool
        Whether the permissions of the bot should be checked, defaults to True
    perms : dict
        The permissions to check for

    Raises
    ------
    InsufficientPermissions
        If the bot does not have all required permissions
    MissingPermissions
        If the user does not have all required permissions
    """
    def decorator(func):
        return func
    return decorator


def bot_has_permissions(**perms):
    def decorator(func):
        return func
    return decorator
