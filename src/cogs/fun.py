import discord
from discord.ext import commands
import random
import logging

logger = logging.getLogger("discord_bot")

class FunCog(commands.Cog):
    """Fun and entertainment commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="joke", help="Tell a random joke")
    async def joke(self, ctx):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't eggs tell jokes? They'd crack each other up!",
        ]
        
        embed = discord.Embed(
            title="😄 Random Joke",
            description=random.choice(jokes),
            color=discord.Color.yellow(),
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="8ball", help="Ask the magic 8-ball")
    async def eightball(self, ctx, *, question):
        """Ask the magic 8-ball a question"""
        responses = [
            "Yes", "No", "Maybe", "Ask again later",
            "Definitely", "Don't count on it", "Very likely",
            "Outlook not good", "Signs point to yes"
        ]
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {random.choice(responses)}",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="dice", help="Roll a dice")
    async def dice(self, ctx, sides: int = 6):
        """Roll a dice"""
        if sides < 2:
            await ctx.send("❌ Dice must have at least 2 sides")
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{sides}-sided dice**!\n**Result:** {result}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="flip", help="Flip a coin")
    async def flip(self, ctx):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"**Result:** {result}",
            color=discord.Color.greyple(),
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="choose", help="Choose between options")
    async def choose(self, ctx, *options):
        """Choose between options"""
        if len(options) < 2:
            await ctx.send("❌ Provide at least 2 options")
            return
        
        choice = random.choice(options)
        
        embed = discord.Embed(
            title="🎯 Choice Maker",
            description=f"**Options:** {', '.join(options)}\n**Chosen:** {choice}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="say", help="Make the bot say something")
    async def say(self, ctx, *, text):
        """Make the bot say something"""
        await ctx.message.delete()
        await ctx.send(text)

async def setup(bot):
    await bot.add_cog(FunCog(bot))
