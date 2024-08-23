import re
import asyncio
import os
import spotipy
import discord
from yt_dlp import YoutubeDL
from spotipy.oauth2 import SpotifyClientCredentials

class Music:
    """
    A class that manages music data logic, including handling a queue of songs, 
    connecting to the Spotify API, and configuring FFMPEG streaming options.

    Attributes:
    ----------
    sp : spotipy.Spotify
        An instance of the Spotipy client that is authenticated and used to 
        interact with the Spotify Web API.

    FFMPEG_OPTIONS : dict
        A dictionary containing the options for FFMPEG, which is used to stream 
        audio. The options include reconnecting which is important for audio to not cut out early.
    
    YDL_OPTS : dict
        A dictionary containing the options for YouTubeDL.

    song_queue : list
        A list where each element is a dictionary containing metadata for a song.
        Each dictionary has the following structure:
        - 'title' (str): The title of the song.
        - 'artist' (str): The name of the artist.
        - 'url' (str): The YouTube URL of the song.
        - 'thumbnail' (str): The URL of the song's thumbnail image.

    toggle_autoqueue : bool
        A boolean flag indicating whether the autoqueue feature is enabled. When enabled,
        the bot will automatically add songs to the queue based on the currently playing track.
    """
    def __init__(self):
        """
        Initialize the Music class with Spotify API and YouTubeDL configurations.
        """
        # Set up Spotify Web API client
        spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
        spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

        auth_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                client_secret=spotify_client_secret)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # FFMPEG streaming options
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        
        # YouTubeDL options
        YDL_OPTS = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch',
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,
        }
        self.ydl = YoutubeDL(YDL_OPTS)
        
        # Initialize song queue and autoqueue toggle
        self.song_queue = []
        self.toggle_autoqueue = False
        
        # Regular expressions for matching YouTube and Spotify URLs
        self.youtube_url_pattern = r"^https:\/\/www\.youtube\.com\/watch\?v=[\w-]+$"
        self.spotify_url_pattern = r"^https:\/\/open\.spotify\.com\/(track|album|playlist)\/[\w-]+(\?.*)?$"

        # Regular expressions for parsing song titles
        self.title_patterns = [
            r'(.+?)\s*-\s*([^\(]+)',  # Format: "Artist - Song Title"
            r'(.+?)\s*feat\.\s*([^ ]+)',  # Format: "Artist - Song Title feat. Artist"
            r'(.+?)\s*-\s*([^ ]+)\s*\(.*\)',  # Format: "Artist - Song Title (Extra Info)"
        ]

    async def play_song(self, ctx, search):
        """
        Handle the input search query to play a song. It can be a YouTube URL, a Spotify URL, or a search query.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        search : str
            The search query or URL to find the song.
        """
        if re.match(self.youtube_url_pattern, search):
            await self.queue_youtube_url(ctx, search)  
               
        elif re.match(self.spotify_url_pattern, search):
            await self.handle_spotify_link(ctx, search)
            
        else:
            # Treat input as a search query
            url = self.search_youtube(search)
            
            # Add to queue
            if url:
                await self.queue_youtube_url(ctx, url)
            else:
                await ctx.send("Could not find a video matching your search.")
                return

        # If nothing is currently playing, start the playback
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def handle_spotify_link(self, ctx, spotify_url):
        """
        Handle Spotify URLs by fetching track details and searching for the corresponding YouTube video.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        spotify_url : str
            The Spotify URL to handle.
        """
        # Parse album / playlist / track ID from the Spotify URL
        url_id = spotify_url.split('/')[-1].split('?')[0]
        
        # Determine the type of Spotify link
        if 'track' in spotify_url:
            track = self.sp.track(url_id)
            query = f"{track['name']} {track['artists'][0]['name']}"
            youtube_url = self.search_youtube(query)
            if youtube_url:
                await self.queue_youtube_url(ctx, youtube_url)
                
        elif 'album' in spotify_url:
            album = self.sp.album(url_id)
            for track in album['tracks']['items']:
                query = f"{track['name']} {track['artists'][0]['name']}"
                youtube_url = self.search_youtube(query)
                if youtube_url:
                    await self.queue_youtube_url(ctx, youtube_url)

        elif 'playlist' in spotify_url:
            playlist = self.sp.playlist(url_id)
            for item in playlist['tracks']['items']:
                track = item['track']
                query = f"{track['name']} {track['artists'][0]['name']}"
                youtube_url = self.search_youtube(query)
                if youtube_url:
                    await self.queue_youtube_url(ctx, youtube_url)
                    
    async def queue_youtube_url(self, ctx, url):
        """
        Queue a YouTube URL by extracting metadata and adding it to the song queue.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        url : str
            The YouTube URL to queue.
        """
        info_dict = self.ydl.extract_info(url, download=False)
        fetched_url = info_dict.get('url', None)
        video_title = info_dict.get('title', None)
        thumbnail_url = info_dict.get('thumbnail', None)
        metadata = {
            'title': video_title,
            'url': fetched_url,
            'thumbnail': thumbnail_url,
        }
            
        self.song_queue.append(metadata)
        embed = discord.Embed(title="Added to queue", colour=discord.Colour.red())
        embed.set_thumbnail(url=metadata['thumbnail'])
        embed.add_field(name='', value=metadata['title'], inline=True)
        await ctx.send(embed=embed)
    
    async def autoqueue_song(self, ctx, video_title):
        """
        Automatically queue a song based on the last played song using recommendations.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        video_title : str
            The title of the last played song.
        """
        artist = None
        song = None

        # Loop through the patterns until a match is found
        for pattern in self.title_patterns:
            match = re.match(pattern, video_title)
            if match:
                artist, song = match.groups()
                break

        if not artist or not song:
            await ctx.send("Could not parse title for autoqueue.")
            return
            
        # Get a recommended song from Spotify
        recommended_song = self.get_recommendation(song.strip(), artist.strip())
        
        if recommended_song:
            # Search for the song on YouTube
            search_query = f"{recommended_song['artist']} {recommended_song['song']}"
            youtube_url = self.search_youtube(search_query)

            if youtube_url:
                # Add the YouTube URL to the song queue
                await self.queue_youtube_url(ctx, youtube_url)
            else:
                await ctx.send(f"Could not find a YouTube video for {song} by {artist}.")
        else:
            await ctx.send("Could not find a recommendation to autoqueue based on the last played song.")
    
    def search_youtube(self, query):
        """
        Search for a YouTube video based on a query and return the URL of the first result.

        Parameters:
        ----------
        query : str
            The search query for YouTube.

        Returns:
        -------
        str
            The URL of the first YouTube video result.
        """
        info_dict = self.ydl.extract_info(query, download=False)
        if 'entries' in info_dict:
            video = info_dict['entries'][0]  # Take the first result
            return f"https://www.youtube.com/watch?v={video['id']}"
        else:
            return None
    
    def get_recommendation(self, track_name, artist_name):
        """
        Get a song recommendation from Spotify based on a track and artist.

        Parameters:
        ----------
        track_name : str
            The name of the track.
        artist_name : str
            The name of the artist.

        Returns:
        -------
        dict
            A dictionary containing the recommended song's artist and title, or None if no recommendation is found.
        """
        results = self.sp.search(q=f'track:{track_name} artist:{artist_name}', type='track', limit=1)
        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            recommendations = self.sp.recommendations(seed_tracks=[track_id], limit=1)
            if recommendations['tracks']:
                recommended_track = recommendations['tracks'][0]
                recommended_artist = recommended_track['artists'][0]['name']
                recommended_song = recommended_track['name']
                return {
                    'artist': recommended_artist,
                    'song': recommended_song
                }
                
        return None
    
    async def autoqueue(self, ctx):
        """
        Toggle the autoqueue feature on or off.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        """
        if ctx.voice_client:
            self.toggle_autoqueue = not self.toggle_autoqueue
            
            if self.toggle_autoqueue:
                await ctx.send("Autoqueue enabled. I will automatically queue a song based on the last played song.")
            else:
                await ctx.send("Autoqueue disabled.")
        else:
            await ctx.send("I'm not in a voice channel.")
            
    async def play_next(self, ctx):
        """
        Play the next song in the queue. If autoqueue is enabled, add a recommended song based on the last played song.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        """
        if len(self.song_queue) > 0:
            song_metadata = self.song_queue.pop(0)

            embed = discord.Embed(title="Now Playing", colour=discord.Colour.red())
            embed.set_thumbnail(url=song_metadata['thumbnail'])
            embed.add_field(name='', value=song_metadata['title'], inline=True)
            
            ctx.voice_client.play(discord.FFmpegPCMAudio(song_metadata['url'], **self.FFMPEG_OPTIONS),
                                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), ctx.bot.loop))
            await ctx.send(embed=embed)
            
            # Autoqueue a song based on the last played song
            if self.toggle_autoqueue and len(self.song_queue) == 0:
                await self.autoqueue_song(ctx, song_metadata['title'])
        else:
            await ctx.send("The queue is empty!")
            await ctx.voice_client.disconnect()
            
    async def queue(self, ctx):
        """
        Send an embed message showing the current song queue.

        Parameters:
        ----------
        ctx : discord.ext.commands.Context
            The context of the command being executed.
        """
        if len(self.song_queue) > 0:
            embed = discord.Embed(title="Queue", colour=discord.Colour.red())
            
            for i in range(len(self.song_queue)):
                embed.add_field(name='', value=f'**{i+1}.** {self.song_queue[i]["title"]}', inline=False)

            await ctx.message.delete()
            await ctx.send(embed=embed)
        else:
            await ctx.message.delete()
            await ctx.send("The queue is empty.")
            
    def clear_queue(self, ctx):
        """
        Clear the song queue.
        """
        self.song_queue.clear()
        await ctx.send("The queue was cleared.")
