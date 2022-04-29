import os
import discord
import random

client = discord.Client()

@client.event
async def on_ready():
  print(f"{client.user} logged in")

@client.event
async def on_message(message):
  if message.content.startswith("$test"):
    await message.channel.send("test response")

  if message.content.startswith("$flip"):
    randomInt = random.randint(0, 1)
    if(randomInt == 0):
      await message.channel.send("Heads")
    elif(randomInt == 1):
      await message.channel.send("Tails")
      
my_secret = os.environ['TOKEN']
client.run(my_secret)