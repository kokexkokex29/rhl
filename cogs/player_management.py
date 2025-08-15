"""
Player Management Cog
Handles all player-related slash commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class PlayerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="add_player", description="Add a new player")
    @app_commands.describe(
        name="Name of the player",
        value="Market value in Euros",
        club="Club name (optional)",
        position="Player position (GK, DEF, MID, FWD)",
        age="Player age"
    )
    async def add_player(self, interaction: discord.Interaction, name: str, value: float, club: str = None, position: str = "", age: int = 0):
        """Add a new player to the system"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Create unique player ID
        player_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        
        # Check if player already exists
        if self.db.get_player(player_id):
            await interaction.response.send_message(f"❌ Player '{name}' already exists!", ephemeral=True)
            return
        
        club_id = None
        if club:
            club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
            if not self.db.get_club(club_id):
                await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
                return
        
        if self.db.add_player(player_id, name, value, club_id, position, age):
            embed = discord.Embed(
                title="✅ Player Added Successfully",
                color=discord.Color.green(),
                description=f"**{name}** has been added to the system!"
            )
            embed.add_field(name="💎 Market Value", value=f"€{value:,.2f}", inline=True)
            if club:
                embed.add_field(name="⚽ Club", value=club, inline=True)
            else:
                embed.add_field(name="⚽ Club", value="Free Agent", inline=True)
            if position:
                embed.add_field(name="🎯 Position", value=position, inline=True)
            if age > 0:
                embed.add_field(name="🎂 Age", value=f"{age} years", inline=True)
            
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to add player. Please try again.", ephemeral=True)
    
    @app_commands.command(name="remove_player", description="Remove a player")
    @app_commands.describe(name="Name of the player to remove")
    async def remove_player(self, interaction: discord.Interaction, name: str):
        """Remove a player from the system"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        player_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        player = self.db.get_player(player_id)
        
        if not player:
            await interaction.response.send_message(f"❌ Player '{name}' not found!", ephemeral=True)
            return
        
        if self.db.delete_player(player_id):
            embed = discord.Embed(
                title="🗑️ Player Removed",
                color=discord.Color.red(),
                description=f"**{player['name']}** has been removed from the system!"
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to remove player. Please try again.", ephemeral=True)
    
    @app_commands.command(name="update_player_value", description="Update a player's market value")
    @app_commands.describe(
        name="Name of the player",
        value="New market value in Euros"
    )
    async def update_player_value(self, interaction: discord.Interaction, name: str, value: float):
        """Update player's market value"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        player_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        player = self.db.get_player(player_id)
        
        if not player:
            await interaction.response.send_message(f"❌ Player '{name}' not found!", ephemeral=True)
            return
        
        old_value = player['value']
        
        if self.db.update_player_value(player_id, value):
            embed = discord.Embed(
                title="💎 Player Value Updated",
                color=discord.Color.blue(),
                description=f"**{player['name']}**'s market value has been updated!"
            )
            embed.add_field(name="Previous Value", value=f"€{old_value:,.2f}", inline=True)
            embed.add_field(name="New Value", value=f"€{value:,.2f}", inline=True)
            
            change = value - old_value
            change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            embed.add_field(name="Change", value=f"{change_emoji} €{change:,.2f}", inline=True)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to update player value. Please try again.", ephemeral=True)
    
    @app_commands.command(name="list_players", description="List all players")
    async def list_players(self, interaction: discord.Interaction):
        """List all players in the system"""
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("📋 No players found in this server.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="👥 Players List",
            color=discord.Color.green(),
            description="All registered players in this server"
        )
        
        # Sort by value (descending)
        sorted_players = sorted(guild_players.values(), key=lambda x: x['value'], reverse=True)
        
        for i, player in enumerate(sorted_players[:15]):  # Show top 15
            club_name = "Free Agent"
            if player.get('club_id'):
                club = self.db.get_club(player['club_id'])
                if club:
                    club_name = club['name']
            
            embed.add_field(
                name=f"{i+1}. {player['name']}",
                value=f"💎 €{player['value']:,.2f}\n⚽ {club_name}",
                inline=True
            )
        
        if len(sorted_players) > 15:
            embed.set_footer(text=f"Showing top 15 of {len(sorted_players)} players")
        else:
            embed.set_footer(text=f"Total players: {len(sorted_players)}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="player_info", description="Get detailed information about a player")
    @app_commands.describe(name="Name of the player")
    async def player_info(self, interaction: discord.Interaction, name: str):
        """Get detailed player information"""
        player_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        player = self.db.get_player(player_id)
        
        if not player:
            await interaction.response.send_message(f"❌ Player '{name}' not found!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"⭐ {player['name']} - Player Information",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="💎 Market Value", value=f"€{player['value']:,.2f}", inline=True)
        
        # Club information
        if player.get('club_id'):
            club = self.db.get_club(player['club_id'])
            club_name = club['name'] if club else "Unknown Club"
        else:
            club_name = "Free Agent"
        
        embed.add_field(name="⚽ Current Club", value=club_name, inline=True)
        
        # Get transfer history
        transfers = self.db.get_transfers()
        player_transfers = [t for t in transfers if t['player_id'] == player_id]
        
        if player_transfers:
            embed.add_field(name="🔄 Transfers", value=str(len(player_transfers)), inline=True)
            
            # Show last transfer
            last_transfer = max(player_transfers, key=lambda x: x['date'])
            embed.add_field(
                name="🆕 Last Transfer",
                value=f"€{last_transfer['amount']:,.2f}",
                inline=False
            )
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="free_agents", description="List all free agents (players without clubs)")
    async def free_agents(self, interaction: discord.Interaction):
        """List all free agents"""
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        free_agents = {k: v for k, v in guild_players.items() if not v.get('club_id')}
        
        if not free_agents:
            await interaction.response.send_message("📋 No free agents found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🆓 Free Agents",
            color=discord.Color.orange(),
            description="Players available for transfer"
        )
        
        # Sort by value (descending)
        sorted_agents = sorted(free_agents.values(), key=lambda x: x['value'], reverse=True)
        
        for i, player in enumerate(sorted_agents[:10]):  # Show top 10
            embed.add_field(
                name=f"{i+1}. {player['name']}",
                value=f"💎 €{player['value']:,.2f}",
                inline=True
            )
        
        embed.set_footer(text=f"Total free agents: {len(sorted_agents)}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(PlayerManagement(bot))
