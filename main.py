import os
import discord
import random
import asyncio
import requests
from dotenv import load_dotenv
from discord.ext import commands
from utils.music import Music

class DiscordBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music = Music()

    @commands.Cog.listener()
    async def on_disconnect(self):
        if self.bot.voice_clients:
            for voice_client in self.bot.voice_clients:
                await voice_client.disconnect()

    @commands.command()
    async def hoppon(self, ctx):
        """
        Display a help message with descriptions and usage examples for each command.
        """
        embed = discord.Embed(title="Bot Commands", description="List of available commands and their usage:", colour=discord.Colour.blue())
        
        commands = [
            {"name": "coin", "description": "Flips a coin and displays the result (Heads or Tails).", "usage": "!coin"},
            {"name": "randNum", "description": "Generates a random number between the specified minimum and maximum values.", "usage": "!randNum <min> <max>"},
            {"name": "poll", "description": "Creates a poll with the provided options. Separate options with commas.", "usage": "!poll <option1, option2, ...>"},
            {"name": "salah", "description": "Displays prayer times for a specified city and country.", "usage": "!salah <country> <city>"},
            {"name": "join", "description": "Makes the bot join the voice channel that the user is currently in.", "usage": "!join"},
            {"name": "leave", "description": "Makes the bot leave the voice channel.", "usage": "!leave"},
            {"name": "autoqueue", "description": "Toggles the autoqueue feature, which adds songs to the queue based on the last played song.", "usage": "!autoqueue"},
            {"name": "play", "description": "Plays a song based on the provided search input (YouTube URL, Spotify URL, or search query).", "usage": "!play <search_input>"},
            {"name": "skip", "description": "Skips the currently playing song.", "usage": "!skip"},
            {"name": "queue", "description": "Displays the current song queue.", "usage": "!queue"},
            {"name": "clear", "description": "Clears the song queue.", "usage": "!clear"},
            {"name": "pause", "description": "Pauses the currently playing song.", "usage": "!pause"},
            {"name": "resume", "description": "Resumes the paused song.", "usage": "!resume"},
            {"name": "stop", "description": "Stops the currently playing song and clears the queue.", "usage": "!stop"}
        ]
        
        for cmd in commands:
            embed.add_field(name=f"**{cmd['name']}**", value=f"**Description:** {cmd['description']}\n**Usage:** {cmd['usage']}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def coin(self, ctx):
        randomInt = random.randint(0, 1)
        randomGif = random.randint(1, 7)

        await ctx.send(file=discord.File('coinFlips/coinFlip' + str(randomGif) + '.gif'), delete_after=5)
        await asyncio.sleep(5)

        result = "Heads" if randomInt == 0 else "Tails"
        await ctx.send(result)

    @commands.command()
    async def randNum(self, ctx, min: int, max: int):
        randomInt = random.randint(min, max)
        await ctx.send(randomInt)

    @commands.command()
    async def poll(self, ctx, *, options):
        optionList = options.split(",")
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

        embed = discord.Embed(title='Vote', description='React to the message to vote', colour=discord.Colour.blue())
        author = ctx.message.author
        embed.set_thumbnail(url='https://images.alphacoders.com/927/927310.jpg')
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)

        for x in range(len(optionList)):
            embed.add_field(name='Option ' + emoji[x], value=optionList[x], inline=False)

        message = await ctx.send(embed=embed)

        for x in range(len(optionList)):
            await message.add_reaction(emoji[x])

        await ctx.message.delete()

    @commands.command()
    async def salah(self, ctx, *, contents):
        country, city = contents.split(" ")
        url = f'http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2'
        response = requests.get(url)
        data = response.json()
        prayer_times = data["data"]["timings"]

        embed = discord.Embed(title=f"Prayer times for {city}, {country}", colour=discord.Colour.blue())
        embed.set_footer(text='')
        embed.set_thumbnail(url="https://www.ancient-origins.net/sites/default/files/field/image/The-Kaaba.jpg")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name='Fajr', value=f'{prayer_times["Fajr"]}', inline=False)
        embed.add_field(name='Dhuhr', value=f'{prayer_times["Dhuhr"]}', inline=False)
        embed.add_field(name='Asr', value=f'{prayer_times["Asr"]}', inline=False)
        embed.add_field(name='Maghrib', value=f'{prayer_times["Maghrib"]}', inline=False)
        embed.add_field(name='Isha', value=f'{prayer_times["Isha"]}', inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.command()
    async def autoqueue(self, ctx):
        await self.music.autoqueue(ctx)

    @commands.command()
    async def play(self, ctx, *, search_input):
        if not ctx.voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                return

        await self.music.play_song(ctx, search_input)
        
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await ctx.send("No music is currently playing.")

    @commands.command()
    async def queue(self, ctx):
        await self.music.queue(ctx)

    @commands.command()
    async def clear(self, ctx):
        await self.music.clear_queue(ctx)

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the music.")
        else:
            await ctx.send("No music is currently playing or I'm not connected to a voice channel.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the music.")
        else:
            await ctx.send("Music is not paused or I'm not connected to a voice channel.")
            
    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await self.music.clear_queue()
            await ctx.send("Stopped the music and cleared the queue.")
        else:
            await ctx.send("No music is currently playing.")

# ================== SETUP ==================

# Load environment variables
load_dotenv()

# Set up discord bot
intents = discord.Intents.default()
intents.message_content = True  # Enable intents to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Add Cog
@bot.event
async def on_ready():
    await bot.add_cog(DiscordBot(bot))
    print(f"{bot.user} is now running!")

if __name__ == "__main__":
    # Run bot
    bot_token = os.environ['BOT_TOKEN']
    bot.run(bot_token)
