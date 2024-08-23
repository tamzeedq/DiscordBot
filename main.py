import os
import discord
import random
import asyncio
import requests
import json
from dotenv import load_dotenv
from discord.ext import commands
from utils.music import Music

# ================== SETUP ==================

# Load environment variables
load_dotenv()

# Set up discord bot
intents = discord.Intents.default()
intents.message_content = True  # Enable intents to read message content

client = commands.Bot(command_prefix="!", intents=intents)
bot_token = os.environ['BOT_TOKEN']
music = Music()

@client.event
async def on_ready():
    print(f"{client.user} logged in")
    client.load_extension("dch")
    
# Disconnect the bot when the script is terminated
@client.event
async def on_disconnect():
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

# ================== COMMANDS ==================

@client.command()
async def hoppon(ctx):
    embed = discord.Embed(title='Commands',
                          description='List of commands',
                          colour=discord.Colour.red())

    embed.set_footer(text='Footer')
    embed.set_image(url='https://wallpaperaccess.com/full/1445568.jpg')
    embed.set_thumbnail(url='https://images.alphacoders.com/927/927310.jpg')
    embed.set_author(name=client.user.name)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)

    await ctx.send(embed=embed)

# ================== BASIC COMMANDS ==================

@client.command()
async def coin(ctx):
    randomInt = random.randint(0, 1)
    randomGif = random.randint(1, 7)

    await ctx.send(file=discord.File('coinFlips/coinFlip' + str(randomGif) +
                                     '.gif'),
                   delete_after=5)
    await asyncio.sleep(5)

    if (randomInt == 0):
        await ctx.send("Heads")
    elif (randomInt == 1):
        await ctx.send("Tails")


@client.command()
async def randNum(ctx, min, max):
    randomInt = random.randint(int(min), int(max))

    await ctx.send(randomInt)


@client.command()
async def testEmbed(ctx):
    embed = discord.Embed(title='Title',
                          description='Test description',
                          colour=discord.Colour.red())

    author = ctx.message.author
    userName = author.name

    embed.set_footer(text='Footer')
    embed.set_image(url='https://wallpaperaccess.com/full/1445568.jpg')
    embed.set_thumbnail(url='https://images.alphacoders.com/927/927310.jpg')
    embed.set_author(name=userName, icon_url=author.display_avatar.url)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)

    await ctx.send(embed=embed)


@client.command()
async def poll(ctx, *, options):
    optionList = options.split(",")
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    embed = discord.Embed(title='Vote',
                          description='React to the message to vote',
                          colour=discord.Colour.red())

    author = ctx.message.author
    userName = author.name
    embed.set_thumbnail(url='https://images.alphacoders.com/927/927310.jpg')
    embed.set_author(name=userName, icon_url=author.display_avatar.url)

    for x in range(len(optionList)):
        embed.add_field(name='Option ' + emoji[x],
                        value=optionList[x],
                        inline=False)

    message = await ctx.send(embed=embed)

    for x in range(len(optionList)):
        await message.add_reaction(emoji[x])

    await ctx.message.delete()

# ================== SALAH API COMMAND ==================

@client.command()
async def salah(ctx, *, contents):
    country, city = contents.split(" ")
    url = f' http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2'
    response = requests.get(url)
    data = response.json()
    prayer_times = data["data"]["timings"]

    embed = discord.Embed(title=f"Prayer times for {city}, {country}",
                          colour=discord.Colour.red())

    embed.set_footer(text='')
    embed.set_thumbnail(
        url=
        "https://www.ancient-origins.net/sites/default/files/field/image/The-Kaaba.jpg"
    )
    embed.set_author(name=client.user.name, icon_url=client.user.display_avatar.url)
    embed.add_field(name='Fajr', value=f'{prayer_times["Fajr"]}', inline=False)
    embed.add_field(name='Dhuhr',
                    value=f'{prayer_times["Dhuhr"]}',
                    inline=False)
    embed.add_field(name='Asr', value=f'{prayer_times["Asr"]}', inline=False)
    embed.add_field(name='Maghrib',
                    value=f'{prayer_times["Maghrib"]}',
                    inline=False)
    embed.add_field(name='Isha', value=f'{prayer_times["Isha"]}', inline=False)

    await ctx.send(embed=embed)

# ================== MUSIC COMMANDS ==================

@client.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not connected to a voice channel.")

@client.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel.")

@client.command()
async def autoqueue(ctx):
    await music.autoqueue(ctx)

@client.command()
async def play(ctx, *, search_input):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            return

    await music.play_song(ctx, search_input)
    
@client.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    else:
        await ctx.send("No music is currently playing.")

@client.command()
async def queue(ctx):
    await music.queue(ctx)

@client.command()
async def clear(ctx):
    await music.clear_queue(ctx)

@client.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused the music.")
    else:
        await ctx.send("No music is currently playing or I'm not connected to a voice channel.")

@client.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")
    else:
        await ctx.send("Music is not paused or I'm not connected to a voice channel.")
        
@client.command()
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await music.clear_queue()
        await ctx.send("Stopped the music and cleared the queue.")
    else:
        await ctx.send("No music is currently playing.")


if __name__ == "__main__":
    # Run bot
    client.run(bot_token)
