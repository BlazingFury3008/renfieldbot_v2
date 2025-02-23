import discord
from discord.ext import commands
from discord import app_commands, Interaction
import json
from typing import List
from helper.renfield_sql import Renfield_SQL
from helper.role_requirements import role_check



async def autocomplete_groups(interaction: Interaction, current: str):
    """Gets a list of groups for autocompletion

    Args:
        interaction (Interaction): Discord Interaction Variable
        current (str): _description_

    Returns:
        _type_: Autocomplete Dropdown Info
    """
    db = Renfield_SQL()
    cursor = db.connect()

    cursor.execute("SELECT group_name FROM vote_groups WHERE group_name LIKE %s LIMIT 10", (f"%{current}%",))
    groups = cursor.fetchall()

    db.disconnect()

    return [app_commands.Choice(name=g["group_name"], value=g["group_name"]) for g in groups]


class VoteButtons(discord.ui.View):
    def __init__(self, vote_id: int, options: List[str]):
        super().__init__()
        self.vote_id = vote_id
        for option in options:
            self.add_item(VoteButton(option, vote_id))

class VoteButton(discord.ui.Button):
    def __init__(self, label: str, vote_id: int):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.vote_id = vote_id

    async def callback(self, interaction: Interaction):
        """The callback function for whenever the vote button is clicked

        Args:
            interaction (Interaction): Discord Interaction Variable
        """
        await interaction.response.defer(ephemeral=True)
        db = Renfield_SQL()
        cursor = db.connect()

        try:
            cursor.execute("SELECT is_active FROM votes WHERE id = %s", (self.vote_id,))
            vote = cursor.fetchone()

            if not vote or not vote["is_active"]:
                await interaction.followup.send("This vote has ended!", ephemeral=True)
                return

            user_id = interaction.user.id

            cursor.execute(
                "SELECT * FROM votes_users WHERE vote_id = %s AND user_id = %s",
                (self.vote_id, user_id),
            )
            existing_vote = cursor.fetchone()

            if existing_vote:
                await interaction.followup.send("You have already voted!", ephemeral=True)
            else:
                cursor.execute(
                    "INSERT INTO votes_users (vote_id, user_id, choice) VALUES (%s, %s, %s)",
                    (self.vote_id, user_id, self.label),
                )
                db.commit()
                await interaction.followup.send(f"You voted for {self.label}!", ephemeral=True)

        except Exception as e:
            await interaction.followup.send("An error occurred while processing your vote.", ephemeral=True)
            print(f"Error in voting callback: {e}")

        finally:
            db.disconnect()

class VoteCommands(app_commands.Group):
    
    @app_commands.command(name="new", description="Start a new vote")
    @role_check()
    @app_commands.autocomplete(group=autocomplete_groups)
    async def initiate_vote(self, interaction: Interaction, name: str, options: str, group: str = None):
        """Create a new vote

        Args:
            interaction (Interaction): Discord Interaction Variable
            name (str): Name of the Vote
            options (str): Description of the Topic for vote
            group (str, optional): Group for the Vote topic (EG, AGM2025 etc). Defaults to None.
        """
        await interaction.response.defer(thinking=True)

        options_list = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(options_list) < 2:
            await interaction.followup.send("You must provide at least two options!", ephemeral=True)
            return


        db = Renfield_SQL()
        cursor = db.connect()

        print("Start of ID Check")
        group_id = None
        if group:
            print("Group Is there")
            cursor.execute("SELECT id FROM vote_groups WHERE group_name = %s", (group,))
            group_data = cursor.fetchone()
            if group_data:
                print("Group & ID Exists")
                group_id = group_data["id"]
            else:
                print("Creating Group")
                cursor.execute("INSERT INTO vote_groups (group_name) VALUES (%s)", (group,))
                group_id = cursor.lastrowid
                db.commit()

        print("Inserting into Table")
        cursor.execute("INSERT INTO votes (creator_id, vote_name, options, group_id) VALUES (%s, %s, %s, %s)",
                       (interaction.user.id, name, json.dumps(options_list), group_id))
        print("Inserted Into Table")
        vote_id = cursor.lastrowid
        print("Getting votes ID")
        db.commit()
        db.disconnect()

        await interaction.followup.send(f"New Vote Created: **{name}**\nGroup: {group if group else 'No Group'}", ephemeral=True)

        
    @app_commands.command(name="results", description="Show results of a vote")
    @role_check()
    async def vote_results(self, interaction: Interaction, vote_id: int):
        """Display the results of the vote with vote_id

        Args:
            interaction (Interaction): Discord Interaction Variable
            vote_id (int): ID of the vote to display
        """
        await interaction.response.defer(thinking=True)

        db = Renfield_SQL()
        cursor = db.connect()

        cursor.execute("SELECT vote_name, options FROM votes WHERE id = %s", (vote_id,))
        vote = cursor.fetchone()

        if not vote:
            await interaction.followup.send("Vote not found!", ephemeral=True)
            db.disconnect()
            return

        vote_name = vote["vote_name"]
        options_json = vote["options"]
        options = json.loads(options_json)

        cursor.execute("SELECT choice, COUNT(*) as count FROM votes_users WHERE vote_id = %s GROUP BY choice", (vote_id,))
        vote_results = cursor.fetchall()

        results = {option: 0 for option in options}
        total_votes = 0

        for value in vote_results:
            results[value["choice"]] = value["count"]
            total_votes += value["count"]

        db.disconnect()

        # Find the highest vote count
        max_votes = max(results.values()) if results else 0
        winners = [opt for opt, count in results.items() if count == max_votes]

        # Format the results with **bold winners**
        result_text = "\n".join(
            [f"**{opt}**: {'**' if opt in winners else ''}{results[opt]} votes{'**' if opt in winners else ''}" for opt in options]
        )

        await interaction.followup.send(
            f"# Vote Results for: {vote_name}\n"
            f"{result_text}\n\n"
            f"**Total Votes:** {total_votes}\n"
            f"## Winner: {winners}",
            ephemeral=True
        )

    @app_commands.command(name="end", description="End a vote")
    @role_check()
    async def end_vote(self, interaction: Interaction, vote_id: int):
        """End a vote

        Args:
            interaction (Interaction): Discord Interaction Variable
            vote_id (int): ID of the vote to be ended
        """
        await interaction.response.defer(thinking=True)

        db = Renfield_SQL()
        cursor = db.connect()

        cursor.execute("SELECT creator_id FROM votes WHERE id = %s AND is_active = TRUE", (vote_id,))
        vote = cursor.fetchone()

        if not vote:
            await interaction.followup.send("Vote not found or already ended!", ephemeral=True)
        elif vote["creator_id"] != interaction.user.id:
            await interaction.followup.send("Only the creator can end this vote!", ephemeral=True)
        else:
            cursor.execute("UPDATE votes SET is_active = FALSE WHERE id = %s", (vote_id,))
            db.commit()
            await interaction.followup.send(f"Vote #{vote_id} has ended!")

        db.disconnect()
        await vote_results(self, interaction, vote_id)

    

    @app_commands.command(name="show", description="Re-show an active vote")
    @role_check()
    async def show_vote(self, interaction: Interaction, vote_id: int):
        """Display an active vote

        Args:
            interaction (Interaction): Discord Interaction Variable
            vote_id (int): ID of vote to display
        """
        await interaction.response.defer(thinking=True)

        db = Renfield_SQL()
        cursor = db.connect()

        cursor.execute("SELECT vote_name, options, is_active FROM votes WHERE id = %s", (vote_id,))
        vote = cursor.fetchone()

        if not vote:
            await interaction.followup.send("Vote not found!", ephemeral=True)
            db.disconnect()
            return

        if not vote["is_active"]:
            await interaction.followup.send("This vote has already ended!", ephemeral=True)
            db.disconnect()
            return

        vote_name, options_json = vote["vote_name"], vote["options"]
        options = json.loads(options_json)

        view = VoteButtons(vote_id, options)
        await interaction.followup.send(f"**Vote:** {vote_name}\nClick below to vote:", view=view)

        db.disconnect()
    
    @app_commands.command(name="new_group", description="Create a new vote group")
    @role_check()
    async def new_group(self, interaction: Interaction, group_name: str):
        """Creates a new vote group if it doesn't already exist

        Args:
            interaction (Interaction): Discord Interaction Variable
            group_name (str): Name of the new group
        """
        await interaction.response.defer(thinking=True)

        db = Renfield_SQL()
        cursor = db.connect()

        cursor.execute("SELECT id FROM vote_groups WHERE group_name = %s", (group_name,))
        existing_group = cursor.fetchone()

        if existing_group:
            await interaction.followup.send(f"Group **{group_name}** already exists!", ephemeral=True)
        else:
            cursor.execute("INSERT INTO vote_groups (group_name) VALUES (%s)", (group_name,))
            db.commit()
            await interaction.followup.send(f"Vote group **{group_name}** has been created!", ephemeral=True)

        db.disconnect()
        
        
    @app_commands.command(name="list_groups", description="List all available vote groups")
    @role_check()
    async def list_groups(self, interaction: Interaction):
        """Lists all available vote groups

        Args:
            interaction (Interaction): Discord Interaction Variable
        """
        await interaction.response.defer(thinking=True)

        db = Renfield_SQL()
        cursor = db.connect()

        cursor.execute("SELECT group_name FROM vote_groups")
        groups = cursor.fetchall()

        db.disconnect()

        if not groups:
            await interaction.followup.send("No vote groups found.", ephemeral=True)
            return

        group_list = "\n".join([f"• {g['group_name']}" for g in groups])
        await interaction.followup.send(f"**Available Vote Groups:**\n{group_list}", ephemeral=True)


    @app_commands.command(name="all_results", description="Show results for all votes in a group")
    @role_check()
    @app_commands.autocomplete(group_name=autocomplete_groups)
    async def all_results(self, interaction: Interaction, group_name: str):
        """Display results for all votes in a group

        Args:
            interaction (Interaction): Discord Interaction Variable
            group_name (str): Name of the group to display
        """
        await interaction.response.defer(thinking=True)

        db = Renfield_SQL()
        cursor = db.connect()

        cursor.execute("SELECT id FROM vote_groups WHERE group_name = %s", (group_name,))
        group = cursor.fetchone()

        if not group:
            await interaction.followup.send(f"Group **{group_name}** not found.", ephemeral=True)
            db.disconnect()
            return

        group_id = group["id"]
        cursor.execute("SELECT id, vote_name, options FROM votes WHERE group_id = %s", (group_id,))
        votes = cursor.fetchall()

        if not votes:
            await interaction.followup.send(f"No votes found in group **{group_name}**.", ephemeral=True)
            db.disconnect()
            return

        results_text = f"# **Group Results: {group_name}**\n\n"
        for vote in votes:
            results_text += f"## {vote['vote_name']}\n"

        db.disconnect()
        await interaction.followup.send(results_text, ephemeral=True)
class Voting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(VoteCommands(name="vote"))
        
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: Interaction, error):
        """Handles permission errors and ensures a response is sent."""
        try:
            if isinstance(error, app_commands.CheckFailure):
                # Ensure interaction is not already responded to
                if interaction.response.is_done():
                    await interaction.followup.send("You do not have permission to use this command!", ephemeral=True)
                else:
                    await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
                return  # Exit after handling the error

            elif isinstance(error, app_commands.CommandInvokeError):
                if interaction.response.is_done():
                    await interaction.followup.send("An error occurred while executing the command.", ephemeral=True)
                else:
                    await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
                print(f"CommandInvokeError: {error}")

            else:
                if interaction.response.is_done():
                    await interaction.followup.send("An unknown error occurred.", ephemeral=True)
                else:
                    await interaction.response.send_message("An unknown error occurred.", ephemeral=True)
                print(f"Unknown Error: {error}")

        except discord.errors.InteractionResponded:
            print(f"Interaction already responded: {error}")
        except Exception as e:  # Fix incorrect exception handling
            print(f"Error: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Unexpected error occurred!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Voting(bot))
