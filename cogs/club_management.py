"""
Club Management Cog
Handles all club-related slash commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class ClubManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="add_club", description="Add a new football club")
    @app_commands.describe(
        name="Name of the club",
        budget="Initial budget in Euros (default: 0)"
    )
    async def add_club(self, interaction: discord.Interaction, name: str, budget: float = 0.0):
        """Add a new club to the system"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Use guild ID + name as unique club ID
        club_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        
        # Check if club already exists
        if self.db.get_club(club_id):
            await interaction.response.send_message(f"❌ Club '{name}' already exists!", ephemeral=True)
            return
        
        if self.db.add_club(club_id, name, budget):
            embed = discord.Embed(
                title="✅ Club Added Successfully",
                color=discord.Color.green(),
                description=f"**{name}** has been added to the system!"
            )
            embed.add_field(name="💰 Initial Budget", value=f"€{budget:,.2f}", inline=False)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/53/53283.png")
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to add club. Please try again.", ephemeral=True)
    
    @app_commands.command(name="remove_club", description="Remove a football club")
    @app_commands.describe(name="Name of the club to remove")
    async def remove_club(self, interaction: discord.Interaction, name: str):
        """Remove a club from the system"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        club_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        club = self.db.get_club(club_id)
        
        if not club:
            await interaction.response.send_message(f"❌ Club '{name}' not found!", ephemeral=True)
            return
        
        if self.db.delete_club(club_id):
            embed = discord.Embed(
                title="🗑️ Club Removed",
                color=discord.Color.red(),
                description=f"**{club['name']}** has been removed from the system!"
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to remove club. Please try again.", ephemeral=True)
    
    @app_commands.command(name="list_clubs", description="List all football clubs")
    async def list_clubs(self, interaction: discord.Interaction):
        """List all clubs in the system"""
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_clubs:
            await interaction.response.send_message("📋 No clubs found in this server.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏟️ Football Clubs List",
            color=discord.Color.blue(),
            description="All registered clubs in this server"
        )
        
        for club_id, club_data in guild_clubs.items():
            player_count = len(club_data.get('players', []))
            embed.add_field(
                name=f"⚽ {club_data['name']}",
                value=f"💰 Budget: €{club_data['budget']:,.2f}\n👥 Players: {player_count}",
                inline=True
            )
        
        embed.set_footer(text=f"Total clubs: {len(guild_clubs)}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="club_info", description="Get detailed information about a club")
    @app_commands.describe(name="Name of the club")
    async def club_info(self, interaction: discord.Interaction, name: str):
        """Get detailed club information"""
        club_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
        club = self.db.get_club(club_id)
        
        if not club:
            await interaction.response.send_message(f"❌ Club '{name}' not found!", ephemeral=True)
            return
        
        players = self.db.get_players()
        club_players = [players[pid] for pid in club.get('players', []) if pid in players]
        
        embed = discord.Embed(
            title=f"🏟️ {club['name']} - Club Information",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="💰 Budget", value=f"€{club['budget']:,.2f}", inline=True)
        embed.add_field(name="👥 Total Players", value=str(len(club_players)), inline=True)
        
        if club_players:
            total_value = sum(player['value'] for player in club_players)
            embed.add_field(name="💎 Squad Value", value=f"€{total_value:,.2f}", inline=True)
            
            # Show top 5 most valuable players
            sorted_players = sorted(club_players, key=lambda x: x['value'], reverse=True)[:5]
            players_list = "\n".join([f"• {p['name']} - €{p['value']:,.2f}" for p in sorted_players])
            embed.add_field(name="🌟 Top Players", value=players_list, inline=False)
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/53/53283.png")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ClubManagement(bot))
