import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from helper.role_requirements import role_check

class EventCommands(app_commands.Group):
    """Group for handling event-related commands."""

    @app_commands.command(name="create", description="Create a new Discord event")
    @role_check()
    async def create_event(
        self, 
        interaction: Interaction, 
        name: str, 
        description: str, 
        start_time: str, 
        duration: int,  # Duration in minutes
        location: str = "Discord"
    ):
        """Creates a new Discord event

        Args:
            interaction (Interaction): Discord Interaction Variable
            name (str): Event Name
            description (str): Event Description
            start_time (str): Event Start Time (YYYY-MM-DD HH:MM)
            duration (int): Duration of the Event (Minutes)
        """
        await interaction.response.defer(thinking=True)

        # Parse the provided time
        try:
            event_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except ValueError:
            await interaction.followup.send("Invalid time format. Use `YYYY-MM-DD HH:MM` (24-hour format, UTC).")
            return
        
        end_time = event_time + timedelta(minutes=duration)

        # Create the event
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command must be used in a server.")
                return

            load_dotenv()

            VOICE_CHANNEL = os.getenv("DEFAULT_VOICE_CHANNEL_ID")
            channel = await guild.fetch_channel(VOICE_CHANNEL)
            
            if(channel == None):
                await interaction.followup.send(f"Event Not Created, Channel Does Not Exist {VOICE_CHANNEL}")
                
            event_params = {
                "name":name,
                "description":description,
                "start_time":event_time,
                "end_time":end_time,
                "entity_type":discord.EntityType.external if location != "Discord" else discord.EntityType.voice,
                "privacy_level":discord.PrivacyLevel.guild_only
            }
            
            if(location != "Discord"):
                event_params["location"] = location
            else:
                event_params["channel"] = channel

            event = await guild.create_scheduled_event(**event_params)
            
            await interaction.followup.send(f"Event **{name}** has been created! Start time: {event_time.strftime('%Y-%m-%d %H:%M UTC')}")

        except discord.HTTPException as e:
            await interaction.followup.send(f"Failed to create event: {e}")

    @app_commands.command(name="list", description="List upcoming Discord events")
    async def list_events(self, interaction: Interaction):
        """List all upcoming events in the guild

        Args:
            interaction (Interaction): Discord Interaction Variable
        """
        await interaction.response.defer(thinking=True)
        
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("This command must be used in a server.")
            return

        events = guild.scheduled_events
        if not events:
            await interaction.followup.send("No upcoming events found.")
            return

        embed = discord.Embed(title="Upcoming Events", color=discord.Color.blue())
        for event in events:
            embed.add_field(
                name=event.name,
                value=f"**Starts:** {event.start_time.strftime('%Y-%m-%d %H:%M UTC')}\n**Location:** {event.location if event.location else 'Discord Voice Channel'}\n**Description:** {event.description or 'No description'}\n**ID** {event.id}",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delete", description="Delete an existing Discord event")
    @role_check()
    async def delete_event(self, interaction: Interaction, event_id: str):
        """_summary_

        Args:
            interaction (Interaction): Discord Interaction Variable
            event_id (int): ID of the event to delete
        """
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        if not guild:
            await interaction.followup.send("This command must be used in a server.")
            return

        event = guild.get_scheduled_event(int(event_id))
        if not event:
            await interaction.followup.send("No event found with that ID.")
            return

        try:
            await event.delete()
            await interaction.followup.send(f"Event **{event.name}** has been deleted.")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Failed to delete event: {e}")

    @app_commands.command(name="edit", description="Edit an existing event's details")
    @role_check()
    async def edit_event(
        self, 
        interaction: Interaction, 
        event_id: int, 
        new_name: str = None, 
        new_description: str = None, 
        new_start_time: str = None, 
        new_duration: int = None, 
        new_location: str = None
    ):
        """Edits an existing event's details."""
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        if not guild:
            await interaction.followup.send("This command must be used in a server.")
            return

        event = discord.utils.get(await guild.scheduled_events(), id=event_id)
        if not event:
            await interaction.followup.send("⚠️ No event found with that ID.")
            return

        updates = {}
        if new_name:
            updates["name"] = new_name
        if new_description:
            updates["description"] = new_description
        if new_start_time:
            try:
                new_start = datetime.strptime(new_start_time, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                updates["start_time"] = new_start
            except ValueError:
                await interaction.followup.send("⚠️ Invalid time format. Use `YYYY-MM-DD HH:MM` (UTC).")
                return
        if new_duration and "start_time" in updates:
            updates["end_time"] = updates["start_time"] + timedelta(minutes=new_duration)
        if new_location:
            updates["entity_type"] = (
                discord.GuildScheduledEventEntityType.external if new_location != "Discord" else discord.GuildScheduledEventEntityType.voice
            )
            updates["location"] = new_location if new_location != "Discord" else None

        try:
            await event.edit(**updates)
            await interaction.followup.send(f"✏️ Event **{event.name}** has been updated!")
        except discord.HTTPException as e:
            await interaction.followup.send(f"⚠️ Failed to edit event: {e}")


class Events(commands.Cog):
    """Cog that manages event commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.add_command(EventCommands(name="events"))  # Register the event group

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
