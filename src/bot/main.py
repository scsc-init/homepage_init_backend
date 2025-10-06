import discord
from discord.ext import commands

import pathlib
import json

class SCSCBot(commands.Bot):
    def setData(self, data):
        self.data = data

    async def setup_hook(self):
        for path in pathlib.Path("cogs").glob("*.py"):
            await self.load_extension("cogs." + path.stem)
        await self.tree.sync()

    async def getInviteLink(self, maxAge: int = 300, maxUses: int = 1):
        channel = self.get_guild(int(self.data['serverID'])).get_channel(int(self['channelID']))
        inv = await channel.create_invite(max_age=maxAge, max_uses=maxUses)
        return str(inv)

with open("data/data.json", "r") as f:
    data = json.load(f)

bot = SCSCBot(command_prefix=data["commandPrefix"], intents=discord.Intents.all())
bot.setData(data)
