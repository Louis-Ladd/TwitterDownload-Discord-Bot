import os
import discord
from discord import user
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import Command, cooldown
import tweepy
import uuid
import json

client = commands.Bot(command_prefix="d!")
python_path = os.path.dirname(os.path.realpath(__file__))

try:
    with open(f'{python_path}\\data.json') as f:
        keys = json.load(f)
except FileNotFoundError:
    with open(f'{python_path}\\mydata.json') as f:
        keys = json.load(f)

#API START
consumer_key= keys["consumer_key"]
consumer_secret= keys["consumer_secret"]
token_key= keys["token_key"]
token_secret= keys["token_secret"]

def OAuth():
    try:

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token_key,token_secret)

        return auth

    except Exception as e:
        print(e)
        return None

oauth = OAuth()

api = tweepy.API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
#API STOP


@client.event
async def on_ready():
    print("Bot is online")
    await client.change_presence(activity=discord.Game('Twitters shit ass API'))

@client.command()
@commands.cooldown(1, 30, BucketType.user)
async def download(ctx, in_url):
    url = in_url.split("/")
    status_id = url[len(url) - 1]
    try:
        status = api.get_status(status_id)
        print(dir(status))
        
    except Exception as e:
        await ctx.channel.send("Sorry, but that url didn't work.")
        return

    try:
        video_source_url = status.extended_entities["media"][0]["video_info"]["variants"][0]["url"]
        print(video_source_url)
    except Exception as e:
        await ctx.channel.send("The tweet needs a video dummie!")

    uniuqe_id = uuid.uuid4()
    os.system(f'ffmpeg -i {video_source_url} "{python_path}\\cache\\{uniuqe_id}.mp4" -y')
    
    await ctx.channel.send(file=discord.File(f"{python_path}\\cache\\{uniuqe_id}.mp4"))

    os.remove(f"{python_path}\\cache\\{uniuqe_id}.mp4")

@download.error
async def download_errore_handle(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command works every {round(error.retry_after, 2)} seconds, please wait!')




client.run(keys["discord_id"])