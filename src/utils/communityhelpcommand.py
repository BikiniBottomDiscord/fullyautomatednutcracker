from discord.ext import commands
import itertools
import discord

# rev or dove or anyone else seeing this pls ignore the awful parts and feel freel to change anything - mine


class CommunityHelpCommand(commands.HelpCommand):

    def __init__(self, **options):
        self.sort_commands = options.pop('sort_commands', True)
        self.commands_heading = options.pop('commands_heading', "Commands")
        self.dm_help = options.pop('dm_help', False)
        self.dm_help_threshold = options.pop('dm_help_threshold', 1000)
        self.aliases_heading = options.pop('aliases_heading', "Aliases:")
        self.no_category = options.pop('no_category', 'No Category')
        self.embed = discord.Embed()
        self.paginator = commands.Paginator(suffix=None, prefix=None)

        super().__init__(**options)

    async def send_error_message(self, error):
        pass

    def _add_to_bot(self, bot):
        command = discord.ext.commands.help._HelpCommandImpl(bot.help_command, **bot.help_command.command_attrs)
        bot.add_command(command)
        bot.help_command._command_impl = command

    async def send_pages(self, embed):
        destination = self.get_destination()
        embed.color = self.context.author.color
        await destination.send(embed=embed)

    async def command_not_found(self, string):
        embed = discord.Embed(title=f'Command or cog __"{string}"__ not found!', color=self.context.author.color)
        await self.send_pages(embed)

    def get_opening_note(self):
        return f"Use {self.clean_prefix}help [optional command or category]"

    def get_command_signature(self, command):
        return command.signature

    def add_bot_commands_formatting(self, _commands, heading):
        if _commands:
            joined = ', '.join(c.name for c in _commands)
            self.embed.add_field(name=heading, value=joined, inline=False)

    def get_subcommand_formatting(self, command):
        fmt = f'__**{self.clean_prefix}{command.qualified_name}**__:\n {command.help}' if command.help else f'__**{self.clean_prefix}{command.qualified_name}**__'
        return fmt

    def get_command_formatting(self, command):
        description = None
        signature = None
        aliases = None
        help_ = None
        if command.description:
            description = command.description
        if command.signature:
            signature = self.get_command_signature(command)
        if command.aliases:
            aliases = command.aliases
        if command.help:
            help_ = command.help
        return description, signature, aliases, help_

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        elif self.dm_help is None and len(self.paginator) > self.dm_help_threshold:
            return ctx.author
        else:
            return ctx.channel

    async def prepare_help_command(self, ctx, command=None):
        self.paginator.clear()
        await super().prepare_help_command(ctx, command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()
        if note:
            self.embed.title = note

        no_category = f'{self.no_category}'

        def get_category(command, *, no_category_=no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category_

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)
        _commands = None
        for category, c in to_iterate:
            if category == 'No Category':
                _commands = sorted(c, key=lambda cmd: cmd.name) if self.sort_commands else list(c)
            c = sorted(c, key=lambda c1: c1.name) if self.sort_commands else list(c)
            self.add_bot_commands_formatting(c, category)
        joined = ', '.join(c.qualified_name for c in _commands)
        self.embed.add_field(name='No Category', value=joined, inline=False)

        await self.send_pages(self.embed)

    async def send_cog_help(self, cog):
        bot = self.context.bot
        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()
        if note:
            self.embed.title = note

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if filtered:
            sub_command_formats = []
            for command in filtered:
                fmt = self.get_subcommand_formatting(command)
                if fmt:
                    sub_command_formats.append(fmt)
            self.embed.add_field(name=f'**{cog.qualified_name} {self.commands_heading}**',
                                 value='\n'.join(sub_command_formats))

        await self.send_pages(self.embed)

    async def send_group_help(self, group):
        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            note = self.get_opening_note()
            if note:
                self.embed.title = note

            sub_command_formats = []
            for command in filtered:
                fmt = self.get_subcommand_formatting(command)
                if fmt:
                    sub_command_formats.append(fmt)
            self.embed.add_field(name=f'**{self.commands_heading}**', value='\n'.join(sub_command_formats))

        await self.send_pages(self.embed)

    async def send_command_help(self, command):
        description, signature, aliases, help_ = self.get_command_formatting(command)
        self.embed.title = self.get_opening_note()
        thing = f"{self.clean_prefix}{command.qualified_name}" + ('|' + '|'.join(aliases) + ' ' if aliases else '') + (
            f" {signature}" if signature else '')
        self.embed.add_field(name=thing, value=help_)
        await self.send_pages(self.embed)
