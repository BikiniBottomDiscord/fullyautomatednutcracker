import git

from discord.ext import commands

from utils.common import is_admin


class Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repository = git.cmd.Git("../")

    def cog_check(self, ctx):
        return is_admin(ctx.author)

    @commands.group(invoke_without_command=True)
    async def git(self, ctx):
        await ctx.send_help(self.git)

    @git.command()
    async def pull(self, ctx):
        """Sync the downstream git repo with what is on origin/master."""
        async with ctx.channel.typing():
            result = str(self.repository.pull())
            for chunk in self.chunk_by_newline(result):
                await ctx.channel.send(f"```\n{chunk}\n```")
            await ctx.channel.send(f"Done.")

    @git.command()
    async def status(self, ctx):
        """Get the status of the downstream git repo."""
        async with ctx.channel.typing():
            result = str(self.repository.status())
            for chunk in self.chunk_by_newline(result):
                await ctx.channel.send(f"```\n{chunk}\n```")
            await ctx.channel.send(f"Done.")

    @staticmethod
    def chunk_by_newline(string, chunk_size=1900):
        chunks = []
        current_chunk = ""
        for line in string.split("\n"):
            # Is this line able to be in the chunk size?
            if len(current_chunk + line + "\n") < chunk_size:
                current_chunk += line + "\n"
            # Is the line itself longer than the chunk size?
            elif len(line) > chunk_size:
                if len(current_chunk) > 0:
                    chunks.append(current_chunk)
                    current_chunk = ""
                for subchunk in [line[i: i + chunk_size] for i in range(0, len(line), chunk_size)]:
                    chunks.append(subchunk)
            # Otherwise new chunk
            else:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
        chunks.append(current_chunk)
        return chunks


def setup(bot):
    bot.add_cog(Github(bot))
