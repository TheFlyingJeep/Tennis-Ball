from discord.ext import commands
import youtube_dl
from discord import FFmpegPCMAudio

with open("token.txt") as t:
    token = t.read().strip()
client = commands.Bot(command_prefix="hn ", case_insensitive=True)


@client.event
async def on_ready():
    print("Starting tennis ball bot!")


client.run(token)