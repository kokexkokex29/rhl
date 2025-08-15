"""
Permission utilities for Discord bot
Handles admin permission checking and validation
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

def check_admin(interaction: discord.Interaction) -> bool:
    """Check if user has administrator permissions"""
    try:
        # Check if user has administrator permission
        if interaction.user.guild_permissions.administrator:
            return True
        
        # Check if user is server owner
        if interaction.guild.owner_id == interaction.user.id:
            return True
        
        # Check for specific admin roles (optional)
        admin_role_names = ['Admin', 'Administrator', 'Moderator', 'Staff']
        user_roles = [role.name for role in interaction.user.roles]
        
        for role_name in admin_role_names:
            if role_name in user_roles:
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking admin permissions: {e}")
        return False

def admin_only():
    """Decorator to restrict commands to admins only"""
    async def predicate(interaction: discord.Interaction):
        if not check_admin(interaction):
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command!", 
                ephemeral=True
            )
            return False
        return True
    
    return discord.app_commands.check(predicate)

class PermissionError(commands.CommandError):
    """Custom exception for permission errors"""
    pass

def has_admin_permissions():
    """Commands.check decorator for admin permissions"""
    def predicate(ctx):
        if not ctx.author.guild_permissions.administrator:
            raise PermissionError("Administrator permissions required")
        return True
    return commands.check(predicate)
