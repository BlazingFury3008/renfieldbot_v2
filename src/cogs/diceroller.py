import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random

class DiceRollerCommands(app_commands.Group):
    @app_commands.command(name="roll", description="Roll a number of dice at X difficulty")
    async def roll_dice(self, interaction: Interaction, number_of_dice: int, difficulty: int , speciality: bool, comment: str | None):
        await interaction.response.defer(thinking=True)

        results = [random.randint(1, 10) for _ in range(number_of_dice)]

        # Successes calculation
        successes = 0
        difficulty_penalty = max(0, difficulty - 10)  # Handle extreme difficulty
        difficulty = min(difficulty, 10)  # Ensure difficulty is in valid range

        for roll in results:
            if roll >= difficulty:
                if roll == 10 and speciality:
                    successes += 2  # Double success for 10s if special
                else:
                    successes += 1
            if roll == 1:
                successes -= 1  # 1s count as botches

        successes -= difficulty_penalty  # Apply any penalties

        # Formatting roll results
        roll_text = ", ".join(
            f"~~{x}~~" if x == 1 else
            f"**{x}**" if x == 10 and speciality else
            f"*{x}*" if x >= difficulty else
            str(x)
            for x in results
        )

        # Embed message creation
        embed = discord.Embed(
            title=f"{interaction.user.name}'s Roll",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="Successes", value=str(successes), inline=False)
        embed.add_field(name="Values", value=roll_text, inline=False)
        embed.add_field(name="Difficulty", value=str(difficulty), inline=False)
        embed.set_footer(text="Comment: -")  # Placeholder for additional info

        await interaction.followup.send(embed=embed)
            
            


class DiceRoller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(DiceRollerCommands(name="diceroller"))
        
        
async def setup(bot):
    await bot.add_cog(DiceRoller(bot))