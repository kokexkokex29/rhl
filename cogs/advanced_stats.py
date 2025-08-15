"""
Advanced Statistics Cog
Handles advanced statistics and analytics commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class AdvancedStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="top_players_league", description="Show top players in the league by value")
    @app_commands.describe(limit="Number of players to show (default: 10)")
    async def top_players_league(self, interaction: discord.Interaction, limit: int = 10):
        """Show top players in the league"""
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("📋 No players found.", ephemeral=True)
            return
        
        # Sort by value
        sorted_players = sorted(guild_players.values(), key=lambda x: x['value'], reverse=True)[:limit]
        
        embed = discord.Embed(
            title="🏆 Top Players in League",
            color=discord.Color.gold(),
            description=f"Top {len(sorted_players)} most valuable players"
        )
        
        for i, player in enumerate(sorted_players):
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
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="richest_poorest_clubs", description="Show richest and poorest clubs")
    async def richest_poorest_clubs(self, interaction: discord.Interaction):
        """Show financial extremes"""
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_clubs:
            await interaction.response.send_message("📋 No clubs found.", ephemeral=True)
            return
        
        sorted_clubs = sorted(guild_clubs.values(), key=lambda x: x['budget'], reverse=True)
        
        embed = discord.Embed(
            title="💰 Club Financial Rankings",
            color=discord.Color.blue()
        )
        
        # Richest clubs
        richest = sorted_clubs[:3]
        richest_text = "\n".join([f"{i+1}. {club['name']} - €{club['budget']:,.2f}" for i, club in enumerate(richest)])
        embed.add_field(name="🤑 Richest Clubs", value=richest_text, inline=False)
        
        # Poorest clubs
        if len(sorted_clubs) > 3:
            poorest = sorted_clubs[-3:]
            poorest.reverse()  # Show from poorest to less poor
            poorest_text = "\n".join([f"{len(sorted_clubs)-i}. {club['name']} - €{club['budget']:,.2f}" for i, club in enumerate(poorest)])
            embed.add_field(name="💸 Poorest Clubs", value=poorest_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="transfer_activity_ranking", description="Show clubs by transfer activity")
    async def transfer_activity_ranking(self, interaction: discord.Interaction):
        """Show most active clubs in transfers"""
        transfers = self.db.get_transfers()
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        if not guild_transfers:
            await interaction.response.send_message("📋 No transfer activity found.", ephemeral=True)
            return
        
        # Count transfers per club
        club_activity = {}
        clubs = self.db.get_clubs()
        
        for transfer in guild_transfers:
            # Count for buying club
            if transfer['to_club']:
                club_id = transfer['to_club']
                if club_id not in club_activity:
                    club_activity[club_id] = {'bought': 0, 'sold': 0, 'spent': 0, 'received': 0}
                club_activity[club_id]['bought'] += 1
                club_activity[club_id]['spent'] += transfer['amount']
            
            # Count for selling club
            if transfer['from_club']:
                club_id = transfer['from_club']
                if club_id not in club_activity:
                    club_activity[club_id] = {'bought': 0, 'sold': 0, 'spent': 0, 'received': 0}
                club_activity[club_id]['sold'] += 1
                club_activity[club_id]['received'] += transfer['amount']
        
        # Sort by total transfers
        sorted_activity = sorted(
            club_activity.items(), 
            key=lambda x: x[1]['bought'] + x[1]['sold'], 
            reverse=True
        )
        
        embed = discord.Embed(
            title="🔄 Transfer Activity Rankings",
            color=discord.Color.purple(),
            description="Most active clubs in the transfer market"
        )
        
        for i, (club_id, activity) in enumerate(sorted_activity[:8]):
            club = clubs.get(club_id)
            if club:
                total_transfers = activity['bought'] + activity['sold']
                net_spending = activity['spent'] - activity['received']
                net_emoji = "📈" if net_spending > 0 else "📉" if net_spending < 0 else "➡️"
                
                embed.add_field(
                    name=f"{i+1}. {club['name']}",
                    value=f"🔄 {total_transfers} transfers\n📥 {activity['bought']} bought\n📤 {activity['sold']} sold\n{net_emoji} €{net_spending:,.2f} net",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="league_table", description="Show league table by total club value")
    async def league_table(self, interaction: discord.Interaction):
        """Generate league table by total value"""
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        players = self.db.get_players()
        
        if not guild_clubs:
            await interaction.response.send_message("📋 No clubs found.", ephemeral=True)
            return
        
        # Calculate total values
        club_values = []
        for club_id, club_data in guild_clubs.items():
            club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
            squad_value = sum(player['value'] for player in club_players)
            total_value = club_data['budget'] + squad_value
            
            club_values.append({
                'name': club_data['name'],
                'total_value': total_value,
                'budget': club_data['budget'],
                'squad_value': squad_value,
                'player_count': len(club_players)
            })
        
        # Sort by total value
        sorted_clubs = sorted(club_values, key=lambda x: x['total_value'], reverse=True)
        
        embed = discord.Embed(
            title="🏆 League Table (by Total Value)",
            color=discord.Color.gold(),
            description="Clubs ranked by total value (budget + squad value)"
        )
        
        for i, club in enumerate(sorted_clubs):
            position_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            
            embed.add_field(
                name=f"{position_emoji} {club['name']}",
                value=f"💎 Total: €{club['total_value']:,.2f}\n💰 Budget: €{club['budget']:,.2f}\n👥 Squad: €{club['squad_value']:,.2f} ({club['player_count']} players)",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="compare_clubs", description="Compare two clubs directly")
    @app_commands.describe(
        club1="First club name",
        club2="Second club name"
    )
    async def compare_clubs(self, interaction: discord.Interaction, club1: str, club2: str):
        """Compare two clubs"""
        club1_id = f"{interaction.guild.id}_{club1.lower().replace(' ', '_')}"
        club2_id = f"{interaction.guild.id}_{club2.lower().replace(' ', '_')}"
        
        club1_data = self.db.get_club(club1_id)
        club2_data = self.db.get_club(club2_id)
        
        if not club1_data:
            await interaction.response.send_message(f"❌ Club '{club1}' not found!", ephemeral=True)
            return
        
        if not club2_data:
            await interaction.response.send_message(f"❌ Club '{club2}' not found!", ephemeral=True)
            return
        
        players = self.db.get_players()
        transfers = self.db.get_transfers()
        
        # Calculate squad values and stats
        club1_players = [players[pid] for pid in club1_data.get('players', []) if pid in players]
        club2_players = [players[pid] for pid in club2_data.get('players', []) if pid in players]
        
        club1_squad_value = sum(player['value'] for player in club1_players)
        club2_squad_value = sum(player['value'] for player in club2_players)
        
        club1_total = club1_data['budget'] + club1_squad_value
        club2_total = club2_data['budget'] + club2_squad_value
        
        # Transfer activity
        club1_transfers = [t for t in transfers if t['from_club'] == club1_id or t['to_club'] == club1_id]
        club2_transfers = [t for t in transfers if t['from_club'] == club2_id or t['to_club'] == club2_id]
        
        embed = discord.Embed(
            title=f"⚔️ Club Comparison",
            color=discord.Color.orange(),
            description=f"**{club1_data['name']}** vs **{club2_data['name']}**"
        )
        
        # Comparison stats
        embed.add_field(name="💰 Budget", value=f"{club1_data['name']}: €{club1_data['budget']:,.2f}\n{club2_data['name']}: €{club2_data['budget']:,.2f}", inline=False)
        embed.add_field(name="👥 Squad Size", value=f"{club1_data['name']}: {len(club1_players)} players\n{club2_data['name']}: {len(club2_players)} players", inline=False)
        embed.add_field(name="💎 Squad Value", value=f"{club1_data['name']}: €{club1_squad_value:,.2f}\n{club2_data['name']}: €{club2_squad_value:,.2f}", inline=False)
        embed.add_field(name="🏆 Total Value", value=f"{club1_data['name']}: €{club1_total:,.2f}\n{club2_data['name']}: €{club2_total:,.2f}", inline=False)
        embed.add_field(name="🔄 Transfer Activity", value=f"{club1_data['name']}: {len(club1_transfers)} transfers\n{club2_data['name']}: {len(club2_transfers)} transfers", inline=False)
        
        # Winner determination
        winner = club1_data['name'] if club1_total > club2_total else club2_data['name'] if club2_total > club1_total else "Tie"
        if winner != "Tie":
            embed.add_field(name="🏅 Overall Winner", value=f"**{winner}** (by total value)", inline=False)
        else:
            embed.add_field(name="🏅 Result", value="**Perfect Tie!**", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedStats(bot))