import json
import discord
import asyncio
import random

from discord.ext import commands


class Info(commands.Cog):
    """Useful commands for the Jellyfish Factions"""
    def __init__(self, bot):
        self.bot = bot
        with open("config/faction_questions.json", "r") as fp:
            self.questions = json.load(fp)
        self.quizzing = False

    @commands.command()
    async def quiz(self, ctx):
        """Take a quiz to see which faction you most align with."""
        if not isinstance(ctx.channel, discord.DMChannel) and self.quizzing:
            await ctx.channel.send("Only one quiz can be active at a time. You can also take the quiz in DM!")
            return
        if not isinstance(ctx.channel, discord.DMChannel):
            self.quizzing = True
        await ctx.channel.send("You are about to begin the Jellyfishing Factions Alignment Quiz. Each question will vary in answer from `Strongly Disagree` to `Strongly Agree`. React with the apropriate color to answer the question. You have 1 minute per question, otherwise it will time out.")
        await asyncio.sleep(5)

        faction_score = {'NR': 0, 'DU': 0, 'SG': 0}
        question_emojis = {'🔵': ['sa', 'Strongly Agree'], '🟢': ['a', 'Agree'], '🟠': ['n', 'Neutral'], '🟣': ['d', 'Disagree'], '🔴': ['sd', 'Strongly Disagree']}
        for idx, question in enumerate(self.questions):
            question_message = await ctx.channel.send(embed=discord.Embed(title=f"Question {idx + 1}: " + question, description='\n'.join([e + ' ' + question_emojis[e][1] for e in question_emojis]), color=random.randint(0x000000, 0xffffff)))
            for emoji in question_emojis:
                await question_message.add_reaction(emoji)
            try:
                def check(r: discord.Reaction, u: discord.User):
                    return u.id == ctx.author.id and str(r) in question_emojis and r.message.id == question_message.id
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.channel.send("Your quiz timed out.")
                if not isinstance(ctx.channel, discord.DMChannel):
                    self.quizzing = False
                return
            for faction in self.questions[question][question_emojis[str(reaction)][0]]:
                faction_score[faction] += 1
        results = sorted([(k, v) for k, v in faction_score.items()], key=lambda tup: (tup[1], random.random()), reverse=True)
        faction = results[0][0]
        if faction == 'NR':
            await ctx.channel.send(embed=discord.Embed(color=0x00ffff, title="You lean toward Neptune's Royalty!", description="Congratulations Royal, you seem to side with us!").set_thumbnail(url='https://cdn.discordapp.com/emojis/773275811125264384.png'))
        elif faction == 'SG':
            await ctx.channel.send(embed=discord.Embed(color=0xffa000, title="You lean toward Sniper's Guild!", description="Welcome wild one, you seem to like chaos like us.").set_thumbnail(url='https://cdn.discordapp.com/emojis/773275811364470784.png'))
        elif faction == 'DU':
            await ctx.channel.send(embed=discord.Embed(color=0xff0000, title="You lean toward Droid's Union!", description="Greetings Comrade, you seem to serve the Union.").set_thumbnail(url='https://cdn.discordapp.com/emojis/773275810924593212.png'))
        if not isinstance(ctx.channel, discord.DMChannel):
            self.quizzing = False


def setup(bot):
    bot.add_cog(Info(bot))
