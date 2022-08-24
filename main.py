#discord, youtube_dl, pynacl, requests, spotipy
from discord.ext import commands
import music as p
import hangman as Hms
import discord, math
import valorant as v

with open("token.txt") as t:
    token = t.read().strip()
client = commands.Bot(command_prefix=[":"], case_insensitive=True)


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member == client.user and before.channel is not None and after.channel is None:
        await p.servers[before.channel.guild.id].msgchannel.send("I am leaving you alone I guess :P")
        del p.servers[before.channel.guild.id]


@client.command()
async def hello(ctx):
    await ctx.send("hi there")


@client.command(aliases=["p"])
async def play(ctx, *, url):
    if ctx.guild.id not in p.servers:
        try:
            vc = ctx.author.voice.channel
            await vc.connect()
            p.servers[ctx.guild.id] = p.Servers(ctx.guild, vc, client)
            p.servers[ctx.guild.id].msgchannel = ctx.channel
            await p.find_song_type(url, p.servers[ctx.guild.id])
        except AttributeError:
            await ctx.send("You aren't in a vc :P")
    else:
        vc = ctx.author.voice.channel
        bot = p.servers[ctx.guild.id]
        bot.msgchannel = ctx.channel
        if bot.vc_channel != vc:
            await ctx.send("You are not in the bots vc")
        else:
            await p.find_song_type(url, bot)


@client.command(aliases=["s"])
async def skip(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I'm not in a vc")
    else:
        bot = p.servers[ctx.guild.id]
        if bot.vc_channel != ctx.author.voice.channel:
            await ctx.send("You aren't in the bots vc >:(")
        elif not bot.is_playing:
            await ctx.send("The bot isn't playing anything")
        elif bot.curnum >= len(bot.queue) - 1 and not bot.lq:
            await ctx.send("No song to skip to")
        elif bot.lq and bot.curnum == len(bot.queue) - 1:
            bot.curnum = -1
            ctx.voice_client.stop()
            await ctx.send("Skipping")
        else:
            await ctx.send("Skipping")
            ctx.voice_client.stop()
        bot.msgchannel = ctx.channel


@client.command(aliases=["dc"])
async def leave(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I'm not in a vc")
    else:
        bot = p.servers[ctx.guild.id]
        if bot.vc_channel != ctx.author.voice.channel:
            await ctx.send("You aren't in the bots vc >:(")
        else:
            await ctx.voice_client.disconnect()


@client.command(aliases=["np"])
async def nowplaying(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I'm not in a vc")
    else:
        bot = p.servers[ctx.guild.id].queue[p.servers[ctx.guild.id].curnum]
        await ctx.send(bot.url)
        bot.msgchannel = ctx.channel


@client.command(aliases=["q"])
async def queue(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I am not in a vc right now")
    else:
        bot = p.servers[ctx.guild.id]
        try:
            page = int(ctx.message.content.split()[1])
            if page > math.ceil(len(bot.queue)/10) or page < 1:
                await ctx.send("Your value must be in the appropriate range")
            else:
                out = "```Current queue:\n"
                for i in range((page - 1) * 10, (page) * 10):
                    if i == bot.curnum:
                        out += "<Now playing> "
                    try:
                        out += str(i + 1) + ": " + bot.queue[i].title + " " + str(bot.queue[i].durationmins) + ":"
                        if len(str(bot.queue[i].durationsecs)) == 1:
                            out += "0" + str(bot.queue[i].durationsecs)
                        else:
                            out += str(bot.queue[i].durationsecs)
                        out += "\n"
                    except IndexError:
                        break
                out += "Looping: " + str(bot.is_looping) + ", Looping queue: " + str(bot.lq) + "\n"
                out += "```"
                await bot.msgchannel.send(out)
        except ValueError:
            await ctx.send("Provide a number")
        except IndexError:
            out = "```Current queue:\n"
            for i in range((math.floor(bot.curnum / 10) * 10), ((math.floor(bot.curnum / 10) + 1) * 10)):
                if i == bot.curnum:
                    out += "<Now playing> "
                try:
                    out += str(i + 1) + ": " + bot.queue[i].title + " " + str(bot.queue[i].durationmins) + ":"
                    if len(str(bot.queue[i].durationsecs)) == 1:
                        out += "0" + str(bot.queue[i].durationsecs)
                    else:
                        out += str(bot.queue[i].durationsecs)
                    out += "\n"
                except IndexError:
                    break
            out += "Looping: " + str(bot.is_looping) + ", Looping queue: " + str(bot.lq) + "\n"
            out += "```"
            await bot.msgchannel.send(out)


@client.command()
async def loop(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I am not in a vc rn!")
    elif ctx.author.voice.channel != p.servers[ctx.guild.id].vc_channel:
        await ctx.send("You are not in the bots vc")
        p.servers[ctx.guild.id].msgchannel = ctx.channel
    else:
        if p.servers[ctx.guild.id].is_looping:
            await ctx.send("Looping now off!")
            p.servers[ctx.guild.id].is_looping = False
        else:
            await ctx.send("Now looping!")
            p.servers[ctx.guild.id].is_looping = True
            if not p.servers[ctx.guild.id].is_playing:
                p.servers[ctx.guild.id].curnum -= 1
                p.servers[ctx.guild.id].play_song()
        p.servers[ctx.guild.id].msgchannel = ctx.channel


@client.command(aliases=["lq"])
async def loopqueue(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I am not in a vc rn")
    elif ctx.author.voice.channel != p.servers[ctx.guild.id].vc_channel:
        await ctx.send("You are not in the bots vc")
        p.servers[ctx.guild.id].msgchannel = ctx.channel
    else:
        bot = p.servers[ctx.guild.id]
        if bot.lq:
            bot.lq = False
            await ctx.send("No longer looping queue")
        else:
            bot.lq = True
            await ctx.send("Now looping queue")
            if not bot.is_playing:
                bot.curnum -= 1
                bot.play_song()
        bot.msgchannel = ctx.channel


@client.command(aliases=["j"])
async def jump(ctx):
    if ctx.guild.id not in p.servers:
        await ctx.send("I am not in a vc rn!")
    elif ctx.author.voice.channel != p.servers[ctx.guild.id].vc_channel:
        await ctx.send("You are not in the bots vc")
        p.servers[ctx.guild.id].msgchannel = ctx.channel
    else:
        try:
            num = int(ctx.message.content.split()[2])
        except IndexError:
            await ctx.send("Provide a value to jump to")
        except ValueError:
            await ctx.send("Provide a NUMBER")
        else:
            bot = p.servers[ctx.guild.id]
            if num not in range(1, len(bot.queue) + 1):
                await ctx.send("Provide a valid number.")
            else:
                bot.curnum = num - 2
                if bot.is_playing:
                    ctx.voice_client.stop()
                await ctx.send("Jumping...")
        p.servers[ctx.guild.id].msgchannel = ctx.channel


@client.command()
async def hangman(ctx, player2: discord.Member):
    if player2.id in Hms.games:
        await ctx.send("That user is already playing a game!")
    else:
        await Hms.startgame(client, ctx, player2)


@client.command()
async def guess(ctx):
    if ctx.author.id not in Hms.games:
        await ctx.send("You are not playing a game rn")
        return
    try:
        guess = ctx.message.content.split()[1]
        await Hms.runguess(ctx, guess.lower())
    except IndexError:
        await ctx.send("Put an actual guess")


@client.event
async def on_ready():
    print("Starting tennis ball bot!")


@client.command()
async def lineup(ctx):
    params = ctx.message.content.lower().split()
    try:
        agent, _map, site = params[1], params[2], params[3]
        await v.fetchLineup(ctx, _map, agent, site)
    except IndexError:
        await ctx.send("The correct format is: \n :lineup {agent} {map} {site}")


client.run(token)