# Hoppon - Discord Server Bot
Hoppon is a play on the saying "hop on", as I originally created this bot for the convenience of my personal discord server with friends. Because of this, the features that the bot supports are tailored to our needs such as playing music and creating polls, but feel free to clone the repo and add any features that you would like. 

**Technologies**
- Python 3.11 or greater 
- Docker
- FFmpeg

## Setup
Start by cloning the respository and you will then need to create a `.env` file with the same format as below

```
BOT_TOKEN = ...
SPOTIFY_CLIENT_ID = ...
SPOTIFY_CLIENT_SECRET = ...
```
> The ... are to be filled with your personal tokens and secrets

### Download FFmpeg
FFmpeg is a free software that is required for the discord bot to stream audio files into the voice channels. Follow the following links to see where to [Download](https://www.ffmpeg.org/download.html) and how to [Setup](https://www.wikihow.com/Install-FFmpeg-on-Windows) FFmpeg.

### Getting a Discord Bot Token and joining your server

Follow the link to the [Discord Developer Portal](https://discord.com/developers/applications) and sign in with your account, or make an account if you don't already have one.
Click **New Application** to name and create your bot. 

Navigate to the **Bot** menu on the navigation menu and find the token for your bot. This is the token you will use for your `.env` file such that it becomes, for example, `BOT_TOKEN = '123abc'`. 

> Keep your token somewhere safe as you can only view it once and you'll have to generate a new one if you lose it

You may also want to disable **Public Bot** such that only you can add your bot to servers. You can also customize your bot's profile picture, banner, and name here. Next, navigate to **OAuth2** on the menu bar and generate a bot url at the bottom. Copy and paste this URL on your browser and you will then be prompted to invite your bot to a server of your choice.


### Getting a Spotify Client ID and Secret
Follow the link to the [Spotify Developer](https://developer.spotify.com/dashboard) page and sign in with your account. Click **Create App** to create a new app, then inside your app go click **Settings**. Here, under **Basic Information**, you will find your *Client ID* and you can view your *Client Secret* which you will need to for your `.env` file.

### Virtual Environment (Optional)

Running the project in a virtual environment may be ideal to avoid conflicts.

To create an environment, clone the repo and inside the directory run the following:

```
python -m venv env
```

**"env"** can be replaced with whatever you would like to name the environment.


After creating the environment run either of the following to activate the environment:

For Windows
```
env\Scripts\activate
```

For Unix or Mac OS
```
source env/bin/activate
```

### Install Dependencies

To install the required dependencies run the following either in the project directory or in a virtual environment:

```
pip install -r requirements.txt
```
## Run 
To run the program run the following either in the project directory or in a virtual environment:

``` 
python main.py
```

Or:
```
python3 main.py
```

## Docker

Create a docker image for the bot by entering the following into your terminal:

> You can replace `hoppon` with whatever name you like

```
docker build -t hoppon . 
```

To run the image in a container run:

```
docker run -d --name bot_container hoppon 
```

To stop the running container run:

```
docker stop bot_container
```




