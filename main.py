import os
import discord
import random
import asyncio
import requests
import json

#import music
from discord.ext import commands

client = commands.Bot(command_prefix="$")

# cogs = [music]

# for i in range(len(cogs)):
#   cogs[i].setup(client)


@client.event
async def on_ready():
    print(f"{client.user} logged in")
    client.load_extension("dch")


# @client.event
# async def on_message(message):
#   if message.content.startswith("chauffeur"):
#     await message.channel.send("bruh not this again")


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
    embed.set_author(name=userName, icon_url=author.avatar_url)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)

    await ctx.send(embed=embed)


@client.command()
async def poll(ctx, *, options):
    optionList = options.split(" ")
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    embed = discord.Embed(title='Vote',
                          description='React to the message to vote',
                          colour=discord.Colour.red())

    author = ctx.message.author
    userName = author.name
    embed.set_thumbnail(url='https://images.alphacoders.com/927/927310.jpg')
    embed.set_author(name=userName, icon_url=author.avatar_url)

    for x in range(len(optionList)):
        embed.add_field(name='Option ' + emoji[x],
                        value=optionList[x],
                        inline=False)

    message = await ctx.send(embed=embed)

    for x in range(len(optionList)):
        await message.add_reaction(emoji[x])

    await ctx.message.delete()


@client.command()
async def hoppon(ctx):
    embed = discord.Embed(title='Commands',
                          description='List of commands',
                          colour=discord.Colour.red())

    embed.set_footer(text='Footer')
    embed.set_image(url='https://wallpaperaccess.com/full/1445568.jpg')
    embed.set_thumbnail(url='https://images.alphacoders.com/927/927310.jpg')
    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)
    embed.add_field(name='Field Name', value='Field Value', inline=False)

    await ctx.send(embed=embed)


@client.command()
async def salah(ctx, *, contents):
    country, city = contents.split(" ")
    url = f' http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2'
    response = requests.get(url)
    data = response.json()
    print(data)
    prayer_times = data["data"]["timings"]

    embed = discord.Embed(title=f"Prayer times for {city}, {country}",
                          colour=discord.Colour.red())

    embed.set_footer(text='')
    embed.set_thumbnail(
        url=
        "https://www.ancient-origins.net/sites/default/files/field/image/The-Kaaba.jpg"
    )
    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
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


my_secret = os.environ['TOKEN']
client.run(my_secret)
