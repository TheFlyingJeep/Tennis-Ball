from random import randint
import json


with open("lineups.json") as lines:
    data = json.loads(lines.read())


async def fetchLineup(ctx, _map, agent, site):
    try:
        lineupList = data[agent][_map][site]
        lineup = lineupList[randint(0, len(lineupList) - 1)]
        await ctx.send(lineup)
    except KeyError:
        await ctx.send("There is not a lineup for that combination")