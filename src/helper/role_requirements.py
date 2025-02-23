import discord
from discord import app_commands, Interaction
import os
from dotenv import load_dotenv

def role_check():
    """Check if the user has at least one required role"""
    async def predicate(interaction: Interaction):
        """Check if the user has at least one required role

        Args:
            interaction (Interaction): Discord Interaction Variable

        Raises:
            app_commands.CheckFailure: The User does not possess the correct role

        Returns:
            _type_: The user does have at least one required role
        """
        load_dotenv()
        REQUIRED_ROLES = os.getenv("REQUIRED_ROLES").split(",")
        
        if interaction.guild is None:
            raise app_commands.CheckFailure("This command can only be used in a server!")

        user_roles = [role.name for role in interaction.user.roles]  # Get user roles by name
        if any(role in user_roles for role in REQUIRED_ROLES):
            return True  

        # ✅ Ensure the bot responds before raising an error
        if not interaction.response.is_done():
            await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
        
        raise app_commands.CheckFailure("You do not have permission to use this command!")

    return app_commands.check(predicate)