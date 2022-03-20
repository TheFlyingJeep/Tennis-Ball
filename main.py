#discord, youtube_dl, pynacl
from discord.ext import commands
import youtube_dl
from discord import FFmpegPCMAudio

with open("token.txt") as t:
    token = t.read().strip()
client = commands.Bot(command_prefix=["hn ","nh ","Hn ","hN ","Nh ","nH ","HN ","NH " ], case_insensitive=True)

@client.command()
async def hello(ctx):
    await ctx.send("hi there")
@client.event
async def on_ready():
    print("Starting tennis ball bot!")


client.run(token)