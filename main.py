import os
import discord
import random
import asyncio
import requests
import json
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

# ================== SETUP ==================

# Load environment variables
load_dotenv()

# Set up discord bot
intents = discord.Intents.default()
intents.message_content = True  # Enable intents to read message content

client = commands.Bot(command_prefix="$", intents=intents)
bot_token = os.environ['BOT_TOKEN']

# Set up spotify web api client
spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

auth_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                        client_secret=spotify_client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# FFMPEG options
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


# Hold song queue
# Song Queue = [Song Metadata...]
# Song Metadata = {
#     'title': 'Song Title',
#     'artist': 'Song Artist',
#     'url': 'YouTube URL',
#     'thumbnail': 'Thumbnail URL'
# }
song_queue = []

# Autoqueue toggle
toggle_autoqueue = False

@client.event
async def on_ready():
    print(f"{client.user} logged in")
    client.load_extension("dch")

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
    global toggle_autoqueue
    
    if ctx.voice_client:
        toggle_autoqueue = not toggle_autoqueue
        
        if toggle_autoqueue:
            await ctx.send("Autoqueue enabled. I will automatically queue a song based on the last played song.")
        else:
            await ctx.send("Autoqueue disabled.")
    else:
        await ctx.send("I'm not in a voice channel.")

@client.command()
async def play(ctx, *, search_input):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            return

    youtube_url_pattern = r"^https:\/\/www\.youtube\.com\/watch\?v=[\w-]+$"
    spotify_url_pattern = r"^https:\/\/open\.spotify\.com\/(track|album|playlist)\/[\w-]+(\?.*)?$"

    if re.match(youtube_url_pattern, search_input):
        # Add to queue
        await queue_youtube_url(ctx, search_input)
        
    elif re.match(spotify_url_pattern, search_input):
        await handle_spotify_link(ctx, search_input)
    else:
        # Treat input as a search query
        url = search_youtube(search_input)
        
        # Add to queue
        if url:
            await queue_youtube_url(ctx, url)
        else:
            await ctx.send("Could not find a video matching your search.")
            return

    # If nothing is currently playing, start the playback
    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def handle_spotify_link(ctx, spotify_url):
    # Parse album / playlist / track ID from the Spotify URL
    url_id = spotify_url.split('/')[-1].split('?')[0]
    
    # Determine the type of Spotify link
    if 'track' in spotify_url:
        track = sp.track(url_id)
        query = f"{track['name']} {track['artists'][0]['name']}"
        youtube_url = search_youtube(query)
        if youtube_url:
            await queue_youtube_url(ctx, youtube_url)
            
    elif 'album' in spotify_url:
        album = sp.album(url_id)
        for track in album['tracks']['items']:
            query = f"{track['name']} {track['artists'][0]['name']}"
            youtube_url = search_youtube(query)
            if youtube_url:
                await queue_youtube_url(ctx, youtube_url)

    elif 'playlist' in spotify_url:
        playlist = sp.playlist(url_id)
        for item in playlist['tracks']['items']:
            track = item['track']
            query = f"{track['name']} {track['artists'][0]['name']}"
            youtube_url = search_youtube(query)
            if youtube_url:
                await queue_youtube_url(ctx, youtube_url)


async def queue_youtube_url(ctx, url):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        fetched_url = info_dict.get('url', None)
        video_title = info_dict.get('title', None)
        thumbnail_url = info_dict.get('thumbnail', None)
        metadata = {
            'title': video_title,
            'url': fetched_url,
            'thumbnail': thumbnail_url,
        }
        
    song_queue.append(metadata)
    embed = discord.Embed(title="Added to queue", colour=discord.Colour.red())
    embed.set_thumbnail(url=metadata['thumbnail'])
    embed.add_field(name='', value=metadata['title'], inline=True)
    # await ctx.message.delete()
    await ctx.send(embed=embed)
    

async def play_next(ctx):
    if len(song_queue) > 0:
        song_metadata = song_queue.pop(0)

        embed = discord.Embed(title="Now Playing", colour=discord.Colour.red())
        embed.set_thumbnail(url=song_metadata['thumbnail'])
        embed.add_field(name='', value=song_metadata['title'], inline=True)
        
        ctx.voice_client.play(discord.FFmpegPCMAudio(song_metadata['url'], **FFMPEG_OPTIONS),
                              after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send(embed=embed)
        
        # Autoqueue a song based on the last played song
        if toggle_autoqueue and len(song_queue) == 0:
            await autoqueue_song(ctx, song_metadata['title'])
    else:
        await ctx.send("The queue is empty!")
        await ctx.voice_client.disconnect()
        

# Function to get recommendations based on a track's metadata
def get_recommendation(track_name, artist_name):
    results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track', limit=1)
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        recommendations = sp.recommendations(seed_tracks=[track_id], limit=1)
        if recommendations['tracks']:
            recommended_track = recommendations['tracks'][0]
            recommended_artist = recommended_track['artists'][0]['name']
            recommended_song = recommended_track['name']
            return {
                'artist': recommended_artist,
                'song': recommended_song
            }
    return None

async def autoqueue_song(ctx, video_title):
    # List of regex patterns to try
    title_patterns = [
        r'(.+?)\s*-\s*([^\(]+)',  # Format: "Artist - Song Title"
        r'(.+?)\s*feat\.\s*([^ ]+)',  # Format: "Artist - Song Title feat. Artist"
        r'(.+?)\s*-\s*([^ ]+)\s*\(.*\)',  # Format: "Artist - Song Title (Extra Info)"
    ]

    artist = None
    song = None

    # Loop through the patterns until a match is found
    for pattern in title_patterns:
        match = re.match(pattern, video_title)
        if match:
            artist, song = match.groups()
            break

    if not artist or not song:
        await ctx.send("Could not parse title for autoqueue.")
        return
        
    # Get a recommended song from Spotify
    recommended_song = get_recommendation(song.strip(), artist.strip())
    
    if recommended_song:
        # Search for the song on YouTube
        search_query = f"{recommended_song['artist']} {recommended_song['song']}"
        youtube_url = search_youtube(search_query)

        if youtube_url:
            # Add the YouTube URL to the song queue
            await queue_youtube_url(ctx, youtube_url)
        else:
            await ctx.send(f"Could not find a YouTube video for {song} by {artist}.")
    else:
        await ctx.send("Could not find a recommendation to autoqueue based on the last played song.")

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'skip_download': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(query, download=False)
        if 'entries' in info_dict:
            video = info_dict['entries'][0]  # Take the first result
            return f"https://www.youtube.com/watch?v={video['id']}"
        else:
            return None

@client.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No music is currently playing.")

@client.command()
async def queue(ctx):
    if len(song_queue) > 0:

        embed = discord.Embed(title="Queue", colour=discord.Colour.red())
        
        for i in range(len(song_queue)):
            embed.add_field(name='', value=f'**{i+1}.** {song_queue[i]["title"]}', inline=False)

        await ctx.message.delete()
        await ctx.send(embed=embed)
    else:
        await ctx.message.delete()
        await ctx.send("The queue is empty.")

@client.command()
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        song_queue.clear()
        await ctx.send("Stopped the music and cleared the queue.")
    else:
        await ctx.send("No music is currently playing.")

# Disconnect the bot when the script is terminated
@client.event
async def on_disconnect():
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


if __name__ == "__main__":
    # Run bot
    client.run(bot_token)
