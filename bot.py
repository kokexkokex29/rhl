"""
Discord Football Club Management Bot
Main bot class with slash commands and cogs
"""

import discord
from discord.ext import commands
import logging
import os
from utils.database import Database
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class FootballBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Football Club Management Bot'
        )
        
        self.db = Database()
        
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        cogs = [
            'cogs.club_management',
            'cogs.player_management',
            'cogs.transfer_management',
            'cogs.financial_management',
            'cogs.advanced_stats',
            'cogs.admin_tools',
            'cogs.enhanced_player_management',
            'cogs.extra_commands',
            'cogs.utility_commands',
            'cogs.visual_embeds'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="Managing Football Clubs ⚽"),
            status=discord.Status.online
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ You don't have permission to use this command!", ephemeral=True)
        elif isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        else:
            logger.error(f"Command error: {error}")
            await ctx.respond("❌ An error occurred while processing the command.", ephemeral=True)
