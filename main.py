import os
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import tweepy
import uuid
import json

client = commands.Bot(command_prefix="d!")
python_path = os.path.dirname(os.path.realpath(__file__))

#check cache and json
if os.path.isdir(f"{python_path}\\cache\\") == True:
    print("cache found")
elif os.path.isdir(f"{python_path}\\cache\\") == False:
    print("cache made")
    os.mkdir(f"{python_path}\\cache\\")

if os.environ['COMPUTERNAME'] == "LADD-OVERLORD":
    print("Dev, using unique data")
    with open(f'{python_path}\\mydata.json') as f:
        keys = json.load(f)
else:
    print("non-Dev, using data.json")
    with open(f'{python_path}\\data.json') as f:
        keys = json.load(f)
#check cache and json

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

api = tweepy.API(OAuth(), wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
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
    if "?" in status_id: #removes ?=20s garbage out of urls
        status_id_q = status_id.split("?")
        status_id = status_id_q[0]

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
    await ctx.channel.send("Downloading... Please wait!")
    os.system(f'ffmpeg -i {video_source_url} "{python_path}\\cache\\{uniuqe_id}.mp4" -y')
    prev_msg = await ctx.channel.history().get(author__id=876320913153458196) #Gets prev message
    await prev_msg.delete(delay=0.1)
    await ctx.channel.send(file=discord.File(f"{python_path}\\cache\\{uniuqe_id}.mp4"))

    os.remove(f"{python_path}\\cache\\{uniuqe_id}.mp4")
    


@download.error
async def download_error_handle(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command works every {round(error.retry_after, 2)} seconds, please wait!')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f'This commands requires a URL or ID of a tweet with a video! (example:https://twitter.com/comfortparx/status/1426032422555168769, 1426032422555168769)')
    else:
        print("An Exception has occured!")
        print(error + "\n")
        


client.run(keys["discord_id"])