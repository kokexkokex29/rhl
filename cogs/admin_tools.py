"""
Admin Tools Cog
Additional administrative commands and utilities
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import os
from datetime import datetime
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="rename_club", description="Rename a club")
    @app_commands.describe(
        old_name="Current club name",
        new_name="New club name"
    )
    async def rename_club(self, interaction: discord.Interaction, old_name: str, new_name: str):
        """Rename a club"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        old_club_id = f"{interaction.guild.id}_{old_name.lower().replace(' ', '_')}"
        new_club_id = f"{interaction.guild.id}_{new_name.lower().replace(' ', '_')}"
        
        club_data = self.db.get_club(old_club_id)
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{old_name}' not found!", ephemeral=True)
            return
        
        # Check if new name already exists
        if self.db.get_club(new_club_id):
            await interaction.response.send_message(f"❌ Club '{new_name}' already exists!", ephemeral=True)
            return
        
        # Create new club with same data
        if self.db.add_club(new_club_id, new_name, club_data['budget']):
            # Copy players to new club
            clubs_data = self.db._read_json(self.db.clubs_file)
            clubs_data['clubs'][new_club_id]['players'] = club_data.get('players', [])
            clubs_data['clubs'][new_club_id]['created_at'] = club_data.get('created_at')
            self.db._write_json(self.db.clubs_file, clubs_data)
            
            # Update player assignments
            players_data = self.db._read_json(self.db.players_file)
            for player_id, player in players_data['players'].items():
                if player.get('club_id') == old_club_id:
                    player['club_id'] = new_club_id
            self.db._write_json(self.db.players_file, players_data)
            
            # Update transfer history
            transfers_data = self.db._read_json(self.db.transfers_file)
            for transfer in transfers_data['transfers']:
                if transfer.get('from_club') == old_club_id:
                    transfer['from_club'] = new_club_id
                if transfer.get('to_club') == old_club_id:
                    transfer['to_club'] = new_club_id
            self.db._write_json(self.db.transfers_file, transfers_data)
            
            # Delete old club
            self.db.delete_club(old_club_id)
            
            embed = discord.Embed(
                title="✏️ Club Renamed Successfully",
                color=discord.Color.green(),
                description=f"**{old_name}** has been renamed to **{new_name}**"
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to rename club.", ephemeral=True)
    
    @app_commands.command(name="rename_player", description="Rename a player")
    @app_commands.describe(
        old_name="Current player name",
        new_name="New player name"
    )
    async def rename_player(self, interaction: discord.Interaction, old_name: str, new_name: str):
        """Rename a player"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        old_player_id = f"{interaction.guild.id}_{old_name.lower().replace(' ', '_')}"
        new_player_id = f"{interaction.guild.id}_{new_name.lower().replace(' ', '_')}"
        
        player_data = self.db.get_player(old_player_id)
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{old_name}' not found!", ephemeral=True)
            return
        
        # Check if new name already exists
        if self.db.get_player(new_player_id):
            await interaction.response.send_message(f"❌ Player '{new_name}' already exists!", ephemeral=True)
            return
        
        # Create new player with same data
        if self.db.add_player(new_player_id, new_name, player_data['value'], player_data.get('club_id')):
            # Copy additional data
            players_data = self.db._read_json(self.db.players_file)
            players_data['players'][new_player_id]['position'] = player_data.get('position', '')
            players_data['players'][new_player_id]['age'] = player_data.get('age', 0)
            players_data['players'][new_player_id]['created_at'] = player_data.get('created_at')
            self.db._write_json(self.db.players_file, players_data)
            
            # Update club rosters
            if player_data.get('club_id'):
                clubs_data = self.db._read_json(self.db.clubs_file)
                club_id = player_data['club_id']
                if club_id in clubs_data['clubs']:
                    if old_player_id in clubs_data['clubs'][club_id]['players']:
                        clubs_data['clubs'][club_id]['players'].remove(old_player_id)
                        clubs_data['clubs'][club_id]['players'].append(new_player_id)
                    self.db._write_json(self.db.clubs_file, clubs_data)
            
            # Update transfer history
            transfers_data = self.db._read_json(self.db.transfers_file)
            for transfer in transfers_data['transfers']:
                if transfer.get('player_id') == old_player_id:
                    transfer['player_id'] = new_player_id
            self.db._write_json(self.db.transfers_file, transfers_data)
            
            # Delete old player
            self.db.delete_player(old_player_id)
            
            embed = discord.Embed(
                title="✏️ Player Renamed Successfully",
                color=discord.Color.green(),
                description=f"**{old_name}** has been renamed to **{new_name}**"
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to rename player.", ephemeral=True)
    
    @app_commands.command(name="backup_data", description="Create a backup of all data")
    async def backup_data(self, interaction: discord.Interaction):
        """Create data backup"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        try:
            # Create backup directory
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"backup_{interaction.guild.id}_{timestamp}.json")
            
            # Collect all data
            backup_data = {
                'guild_id': interaction.guild.id,
                'backup_date': datetime.now().isoformat(),
                'clubs': self.db.get_clubs(),
                'players': self.db.get_players(),
                'transfers': self.db.get_transfers()
            }
            
            # Write backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            embed = discord.Embed(
                title="💾 Backup Created",
                color=discord.Color.blue(),
                description=f"Data backup created successfully!"
            )
            embed.add_field(name="Backup File", value=f"`{backup_file}`", inline=False)
            embed.add_field(name="Timestamp", value=timestamp, inline=True)
            embed.add_field(name="Guild ID", value=str(interaction.guild.id), inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            await interaction.response.send_message("❌ Backup failed. Please try again.", ephemeral=True)
    
    @app_commands.command(name="clear_all_data", description="Clear all data (USE WITH CAUTION)")
    @app_commands.describe(confirm="Type 'CONFIRM' to proceed")
    async def clear_all_data(self, interaction: discord.Interaction, confirm: str):
        """Clear all data for this server"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if confirm.upper() != "CONFIRM":
            await interaction.response.send_message("❌ You must type 'CONFIRM' to proceed with data clearing!", ephemeral=True)
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            # Clear clubs
            clubs_data = self.db._read_json(self.db.clubs_file)
            clubs_to_remove = [k for k in clubs_data['clubs'].keys() if k.startswith(guild_id)]
            for club_id in clubs_to_remove:
                del clubs_data['clubs'][club_id]
            self.db._write_json(self.db.clubs_file, clubs_data)
            
            # Clear players
            players_data = self.db._read_json(self.db.players_file)
            players_to_remove = [k for k in players_data['players'].keys() if k.startswith(guild_id)]
            for player_id in players_to_remove:
                del players_data['players'][player_id]
            self.db._write_json(self.db.players_file, players_data)
            
            # Clear transfers
            transfers_data = self.db._read_json(self.db.transfers_file)
            transfers_data['transfers'] = [t for t in transfers_data['transfers'] if not t['player_id'].startswith(guild_id)]
            self.db._write_json(self.db.transfers_file, transfers_data)
            
            embed = discord.Embed(
                title="🗑️ All Data Cleared",
                color=discord.Color.red(),
                description="All clubs, players, and transfer data have been permanently deleted!"
            )
            embed.add_field(name="Clubs Removed", value=str(len(clubs_to_remove)), inline=True)
            embed.add_field(name="Players Removed", value=str(len(players_to_remove)), inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Data clearing failed: {e}")
            await interaction.response.send_message("❌ Failed to clear data. Please try again.", ephemeral=True)
    
    @app_commands.command(name="average_values", description="Show average player values per club")
    async def average_values(self, interaction: discord.Interaction):
        """Calculate average player values"""
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        players = self.db.get_players()
        
        if not guild_clubs:
            await interaction.response.send_message("📋 No clubs found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Average Player Values",
            color=discord.Color.blue(),
            description="Average market value of players per club"
        )
        
        club_averages = []
        
        for club_id, club_data in guild_clubs.items():
            club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
            
            if club_players:
                total_value = sum(player['value'] for player in club_players)
                avg_value = total_value / len(club_players)
                club_averages.append((club_data['name'], avg_value, len(club_players)))
            else:
                club_averages.append((club_data['name'], 0, 0))
        
        # Sort by average value
        club_averages.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, avg_value, player_count) in enumerate(club_averages):
            if player_count > 0:
                embed.add_field(
                    name=f"{i+1}. {name}",
                    value=f"💎 Avg: €{avg_value:,.2f}\n👥 Players: {player_count}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"{i+1}. {name}",
                    value=f"💎 Avg: €0.00\n👥 Players: 0",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clubs_needing_players", description="Show clubs with few players")
    @app_commands.describe(threshold="Minimum player count threshold (default: 5)")
    async def clubs_needing_players(self, interaction: discord.Interaction, threshold: int = 5):
        """Show clubs that need more players"""
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        players = self.db.get_players()
        
        if not guild_clubs:
            await interaction.response.send_message("📋 No clubs found.", ephemeral=True)
            return
        
        clubs_needing_players = []
        
        for club_id, club_data in guild_clubs.items():
            club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
            if len(club_players) < threshold:
                clubs_needing_players.append((club_data['name'], len(club_players), club_data['budget']))
        
        if not clubs_needing_players:
            await interaction.response.send_message(f"✅ All clubs have {threshold}+ players!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔍 Clubs Needing Players",
            color=discord.Color.orange(),
            description=f"Clubs with fewer than {threshold} players"
        )
        
        # Sort by player count (ascending)
        clubs_needing_players.sort(key=lambda x: x[1])
        
        for name, player_count, budget in clubs_needing_players:
            embed.add_field(
                name=f"⚠️ {name}",
                value=f"👥 {player_count} players\n💰 €{budget:,.2f} budget",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="most_transferred_players", description="Show players with most transfers")
    @app_commands.describe(limit="Number of players to show (default: 10)")
    async def most_transferred_players(self, interaction: discord.Interaction, limit: int = 10):
        """Show players with most transfers"""
        transfers = self.db.get_transfers()
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        if not guild_transfers:
            await interaction.response.send_message("📋 No transfer history found.", ephemeral=True)
            return
        
        # Count transfers per player
        player_transfers = {}
        for transfer in guild_transfers:
            player_id = transfer['player_id']
            if player_id not in player_transfers:
                player_transfers[player_id] = 0
            player_transfers[player_id] += 1
        
        # Sort by transfer count
        sorted_players = sorted(player_transfers.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        embed = discord.Embed(
            title="🔄 Most Transferred Players",
            color=discord.Color.purple(),
            description=f"Players with most transfers"
        )
        
        players = self.db.get_players()
        
        for i, (player_id, transfer_count) in enumerate(sorted_players):
            player_data = players.get(player_id)
            if player_data:
                current_club = "Free Agent"
                if player_data.get('club_id'):
                    club = self.db.get_club(player_data['club_id'])
                    if club:
                        current_club = club['name']
                
                embed.add_field(
                    name=f"{i+1}. {player_data['name']}",
                    value=f"🔄 {transfer_count} transfers\n💎 €{player_data['value']:,.2f}\n⚽ {current_club}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminTools(bot))