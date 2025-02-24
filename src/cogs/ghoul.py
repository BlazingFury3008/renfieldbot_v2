import discord
from discord.ext import commands
from discord import app_commands, Interaction
import asyncio
import random
from helper.gpt_connection import gpt_response
import os

class GhoulCommands(app_commands.Group):
    @app_commands.command(name="talk", description="I will respond to your question")
    async def talk(self, interaction: Interaction, message: str):
        await interaction.response.defer(thinking=True)
        response = gpt_response(message, interaction, content=None)
        await interaction.followup.send(response)

class Ghoul(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(GhoulCommands(name="ghoul"))

async def setup(bot):
    await bot.add_cog(Ghoul(bot))
