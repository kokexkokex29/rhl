"""
Enhanced Player Management Cog
Advanced player management features including positions, ages, and contracts
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class EnhancedPlayerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="set_player_position", description="Set a player's position")
    @app_commands.describe(
        player="Player name",
        position="Position (GK, DEF, MID, FWD)"
    )
    async def set_player_position(self, interaction: discord.Interaction, player: str, position: str):
        """Set player position"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        valid_positions = ["GK", "DEF", "MID", "FWD"]
        if position.upper() not in valid_positions:
            await interaction.response.send_message(f"❌ Invalid position! Valid positions: {', '.join(valid_positions)}", ephemeral=True)
            return
        
        player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
        player_data = self.db.get_player(player_id)
        
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{player}' not found!", ephemeral=True)
            return
        
        # Update player position
        players_data = self.db._read_json(self.db.players_file)
        players_data['players'][player_id]['position'] = position.upper()
        self.db._write_json(self.db.players_file, players_data)
        
        embed = discord.Embed(
            title="🎯 Position Updated",
            color=discord.Color.blue(),
            description=f"**{player_data['name']}** position updated to **{position.upper()}**"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="set_player_age", description="Set a player's age")
    @app_commands.describe(
        player="Player name",
        age="Player age"
    )
    async def set_player_age(self, interaction: discord.Interaction, player: str, age: int):
        """Set player age"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if age < 16 or age > 45:
            await interaction.response.send_message("❌ Age must be between 16 and 45!", ephemeral=True)
            return
        
        player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
        player_data = self.db.get_player(player_id)
        
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{player}' not found!", ephemeral=True)
            return
        
        # Update player age
        players_data = self.db._read_json(self.db.players_file)
        players_data['players'][player_id]['age'] = age
        self.db._write_json(self.db.players_file, players_data)
        
        embed = discord.Embed(
            title="🎂 Age Updated",
            color=discord.Color.blue(),
            description=f"**{player_data['name']}** age updated to **{age} years**"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="set_contract_expiry", description="Set player contract expiry date")
    @app_commands.describe(
        player="Player name",
        years="Years until contract expires (default: 2)"
    )
    async def set_contract_expiry(self, interaction: discord.Interaction, player: str, years: int = 2):
        """Set contract expiry"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if years < 1 or years > 10:
            await interaction.response.send_message("❌ Contract length must be between 1 and 10 years!", ephemeral=True)
            return
        
        player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
        player_data = self.db.get_player(player_id)
        
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{player}' not found!", ephemeral=True)
            return
        
        if not player_data.get('club_id'):
            await interaction.response.send_message(f"❌ {player} must be assigned to a club to have a contract!", ephemeral=True)
            return
        
        # Calculate expiry date
        expiry_date = (datetime.now() + timedelta(days=years*365)).isoformat()
        
        # Update contract
        players_data = self.db._read_json(self.db.players_file)
        players_data['players'][player_id]['contract_expires'] = expiry_date
        self.db._write_json(self.db.players_file, players_data)
        
        embed = discord.Embed(
            title="📄 Contract Updated",
            color=discord.Color.green(),
            description=f"**{player_data['name']}** contract set to expire in **{years} year(s)**"
        )
        
        expiry_formatted = datetime.fromisoformat(expiry_date).strftime("%Y-%m-%d")
        embed.add_field(name="Expiry Date", value=expiry_formatted, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="players_by_position", description="List players by position")
    @app_commands.describe(position="Position filter (GK, DEF, MID, FWD)")
    async def players_by_position(self, interaction: discord.Interaction, position: str = None):
        """List players by position"""
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("📋 No players found.", ephemeral=True)
            return
        
        if position:
            position = position.upper()
            filtered_players = {k: v for k, v in guild_players.items() if v.get('position', '').upper() == position}
            if not filtered_players:
                await interaction.response.send_message(f"📋 No {position} players found.", ephemeral=True)
                return
            guild_players = filtered_players
        
        # Group by position
        positions = {"GK": [], "DEF": [], "MID": [], "FWD": [], "": []}
        
        for player_data in guild_players.values():
            pos = player_data.get('position', '')
            if pos in positions:
                positions[pos].append(player_data)
            else:
                positions[''].append(player_data)
        
        embed = discord.Embed(
            title=f"👥 Players by Position" + (f" - {position}" if position else ""),
            color=discord.Color.green()
        )
        
        position_emojis = {"GK": "🥅", "DEF": "🛡️", "MID": "⚽", "FWD": "🎯", "": "❓"}
        position_names = {"GK": "Goalkeepers", "DEF": "Defenders", "MID": "Midfielders", "FWD": "Forwards", "": "Unknown Position"}
        
        for pos, players_list in positions.items():
            if players_list and (not position or pos == position):
                sorted_players = sorted(players_list, key=lambda x: x['value'], reverse=True)
                
                players_text = ""
                for i, p in enumerate(sorted_players[:8]):  # Show top 8 per position
                    club_name = "Free Agent"
                    if p.get('club_id'):
                        club = self.db.get_club(p['club_id'])
                        if club:
                            club_name = club['name'][:12]  # Truncate long names
                    
                    age_text = f" ({p['age']}yo)" if p.get('age', 0) > 0 else ""
                    players_text += f"• {p['name']}{age_text} - €{p['value']:,.0f} - {club_name}\n"
                
                if len(sorted_players) > 8:
                    players_text += f"... and {len(sorted_players) - 8} more"
                
                embed.add_field(
                    name=f"{position_emojis[pos]} {position_names[pos]} ({len(sorted_players)})",
                    value=players_text or "None",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="expiring_contracts", description="Show players with expiring contracts")
    @app_commands.describe(months="Show contracts expiring within X months (default: 6)")
    async def expiring_contracts(self, interaction: discord.Interaction, months: int = 6):
        """Show expiring contracts"""
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("📋 No players found.", ephemeral=True)
            return
        
        # Find players with expiring contracts
        cutoff_date = datetime.now() + timedelta(days=months*30)
        expiring_players = []
        
        for player_data in guild_players.values():
            if player_data.get('contract_expires'):
                try:
                    expiry_date = datetime.fromisoformat(player_data['contract_expires'])
                    if expiry_date <= cutoff_date and expiry_date >= datetime.now():
                        days_remaining = (expiry_date - datetime.now()).days
                        expiring_players.append((player_data, days_remaining))
                except:
                    continue
        
        if not expiring_players:
            await interaction.response.send_message(f"📋 No contracts expiring in the next {months} months.", ephemeral=True)
            return
        
        # Sort by days remaining
        expiring_players.sort(key=lambda x: x[1])
        
        embed = discord.Embed(
            title="📄 Expiring Contracts",
            color=discord.Color.orange(),
            description=f"Contracts expiring within {months} months"
        )
        
        for player_data, days_remaining in expiring_players[:15]:  # Show top 15
            club_name = "Free Agent"
            if player_data.get('club_id'):
                club = self.db.get_club(player_data['club_id'])
                if club:
                    club_name = club['name']
            
            urgency = "🔴" if days_remaining <= 30 else "🟡" if days_remaining <= 90 else "🟢"
            
            embed.add_field(
                name=f"{urgency} {player_data['name']}",
                value=f"⚽ {club_name}\n💎 €{player_data['value']:,.2f}\n📅 {days_remaining} days left",
                inline=True
            )
        
        if len(expiring_players) > 15:
            embed.set_footer(text=f"Showing 15 of {len(expiring_players)} expiring contracts")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="club_squad_analysis", description="Analyze club squad composition")
    @app_commands.describe(club="Club name")
    async def club_squad_analysis(self, interaction: discord.Interaction, club: str):
        """Analyze squad composition"""
        club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
        club_data = self.db.get_club(club_id)
        
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
            return
        
        players = self.db.get_players()
        club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
        
        if not club_players:
            await interaction.response.send_message(f"📋 {club} has no players.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📊 {club_data['name']} - Squad Analysis",
            color=discord.Color.blue()
        )
        
        # Position analysis
        positions = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}
        ages = []
        total_value = 0
        
        for player in club_players:
            pos = player.get('position', '')
            if pos in positions:
                positions[pos] += 1
            
            if player.get('age', 0) > 0:
                ages.append(player['age'])
            
            total_value += player['value']
        
        # Position breakdown
        pos_text = f"🥅 GK: {positions['GK']}\n🛡️ DEF: {positions['DEF']}\n⚽ MID: {positions['MID']}\n🎯 FWD: {positions['FWD']}"
        embed.add_field(name="Squad Composition", value=pos_text, inline=True)
        
        # Basic stats
        embed.add_field(name="👥 Total Players", value=str(len(club_players)), inline=True)
        embed.add_field(name="💎 Squad Value", value=f"€{total_value:,.2f}", inline=True)
        
        # Age analysis
        if ages:
            avg_age = sum(ages) / len(ages)
            embed.add_field(name="🎂 Average Age", value=f"{avg_age:.1f} years", inline=True)
            embed.add_field(name="🎂 Age Range", value=f"{min(ages)} - {max(ages)} years", inline=True)
        
        embed.add_field(name="💰 Available Budget", value=f"€{club_data['budget']:,.2f}", inline=True)
        
        # Squad needs analysis
        needs = []
        if positions['GK'] < 2:
            needs.append("Goalkeepers")
        if positions['DEF'] < 4:
            needs.append("Defenders")
        if positions['MID'] < 3:
            needs.append("Midfielders")
        if positions['FWD'] < 2:
            needs.append("Forwards")
        
        if needs:
            embed.add_field(name="🔍 Squad Needs", value="\n".join([f"• {need}" for need in needs]), inline=False)
        else:
            embed.add_field(name="✅ Squad Status", value="Well-balanced squad", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EnhancedPlayerManagement(bot))