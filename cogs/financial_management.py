"""
Financial Management Cog
Handles club budgets and financial operations
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class FinancialManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="set_budget", description="Set a club's budget")
    @app_commands.describe(
        club="Name of the club",
        budget="New budget amount in Euros"
    )
    async def set_budget(self, interaction: discord.Interaction, club: str, budget: float):
        """Set club budget"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
        club_data = self.db.get_club(club_id)
        
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
            return
        
        old_budget = club_data['budget']
        
        if self.db.update_club_budget(club_id, budget):
            embed = discord.Embed(
                title="💰 Budget Updated",
                color=discord.Color.green(),
                description=f"**{club_data['name']}**'s budget has been updated!"
            )
            
            embed.add_field(name="Previous Budget", value=f"€{old_budget:,.2f}", inline=True)
            embed.add_field(name="New Budget", value=f"€{budget:,.2f}", inline=True)
            
            change = budget - old_budget
            change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            embed.add_field(name="Change", value=f"{change_emoji} €{change:,.2f}", inline=True)
            
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2936/2936525.png")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to update budget. Please try again.", ephemeral=True)
    
    @app_commands.command(name="add_budget", description="Add money to a club's budget")
    @app_commands.describe(
        club="Name of the club",
        amount="Amount to add in Euros"
    )
    async def add_budget(self, interaction: discord.Interaction, club: str, amount: float):
        """Add money to club budget"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
        club_data = self.db.get_club(club_id)
        
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
            return
        
        new_budget = club_data['budget'] + amount
        
        if self.db.update_club_budget(club_id, new_budget):
            embed = discord.Embed(
                title="💰 Budget Increased",
                color=discord.Color.green(),
                description=f"Added €{amount:,.2f} to **{club_data['name']}**'s budget!"
            )
            
            embed.add_field(name="Previous Budget", value=f"€{club_data['budget']:,.2f}", inline=True)
            embed.add_field(name="Amount Added", value=f"€{amount:,.2f}", inline=True)
            embed.add_field(name="New Budget", value=f"€{new_budget:,.2f}", inline=True)
            
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2936/2936525.png")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to add budget. Please try again.", ephemeral=True)
    
    @app_commands.command(name="deduct_budget", description="Deduct money from a club's budget")
    @app_commands.describe(
        club="Name of the club",
        amount="Amount to deduct in Euros"
    )
    async def deduct_budget(self, interaction: discord.Interaction, club: str, amount: float):
        """Deduct money from club budget"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
        club_data = self.db.get_club(club_id)
        
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
            return
        
        new_budget = club_data['budget'] - amount
        
        if new_budget < 0:
            await interaction.response.send_message(
                f"❌ Cannot deduct €{amount:,.2f}. Club only has €{club_data['budget']:,.2f}!",
                ephemeral=True
            )
            return
        
        if self.db.update_club_budget(club_id, new_budget):
            embed = discord.Embed(
                title="💸 Budget Decreased",
                color=discord.Color.red(),
                description=f"Deducted €{amount:,.2f} from **{club_data['name']}**'s budget!"
            )
            
            embed.add_field(name="Previous Budget", value=f"€{club_data['budget']:,.2f}", inline=True)
            embed.add_field(name="Amount Deducted", value=f"€{amount:,.2f}", inline=True)
            embed.add_field(name="New Budget", value=f"€{new_budget:,.2f}", inline=True)
            
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2936/2936525.png")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to deduct budget. Please try again.", ephemeral=True)
    
    @app_commands.command(name="financial_report", description="Generate financial report for all clubs")
    async def financial_report(self, interaction: discord.Interaction):
        """Generate comprehensive financial report"""
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_clubs:
            await interaction.response.send_message("📋 No clubs found for financial report.", ephemeral=True)
            return
        
        players = self.db.get_players()
        transfers = self.db.get_transfers()
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        embed = discord.Embed(
            title="📊 Financial Report",
            color=discord.Color.gold(),
            description="Comprehensive financial overview of all clubs"
        )
        
        total_budget = sum(club['budget'] for club in guild_clubs.values())
        total_spent_transfers = sum(t['amount'] for t in guild_transfers)
        
        embed.add_field(name="💰 Total League Budget", value=f"€{total_budget:,.2f}", inline=True)
        embed.add_field(name="🔄 Total Transfer Spending", value=f"€{total_spent_transfers:,.2f}", inline=True)
        embed.add_field(name="🏟️ Total Clubs", value=str(len(guild_clubs)), inline=True)
        
        # Club rankings by budget
        sorted_clubs = sorted(guild_clubs.values(), key=lambda x: x['budget'], reverse=True)
        
        budget_rankings = ""
        for i, club in enumerate(sorted_clubs[:5]):
            budget_rankings += f"{i+1}. {club['name']} - €{club['budget']:,.2f}\n"
        
        embed.add_field(name="💰 Top 5 Clubs by Budget", value=budget_rankings, inline=False)
        
        # Calculate club values (budget + player values)
        club_values = []
        for club_id, club_data in guild_clubs.items():
            club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
            squad_value = sum(player['value'] for player in club_players)
            total_value = club_data['budget'] + squad_value
            
            club_values.append({
                'name': club_data['name'],
                'total_value': total_value,
                'budget': club_data['budget'],
                'squad_value': squad_value
            })
        
        # Top clubs by total value
        sorted_by_value = sorted(club_values, key=lambda x: x['total_value'], reverse=True)
        
        value_rankings = ""
        for i, club in enumerate(sorted_by_value[:5]):
            value_rankings += f"{i+1}. {club['name']} - €{club['total_value']:,.2f}\n"
        
        embed.add_field(name="💎 Top 5 Clubs by Total Value", value=value_rankings, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="club_finances", description="View detailed finances for a specific club")
    @app_commands.describe(club="Name of the club")
    async def club_finances(self, interaction: discord.Interaction, club: str):
        """View detailed club finances"""
        club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
        club_data = self.db.get_club(club_id)
        
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
            return
        
        players = self.db.get_players()
        club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
        
        transfers = self.db.get_transfers()
        club_transfers = [t for t in transfers if t['from_club'] == club_id or t['to_club'] == club_id]
        
        embed = discord.Embed(
            title=f"💰 {club_data['name']} - Financial Details",
            color=discord.Color.blue()
        )
        
        # Basic finances
        squad_value = sum(player['value'] for player in club_players)
        total_value = club_data['budget'] + squad_value
        
        embed.add_field(name="💵 Available Budget", value=f"€{club_data['budget']:,.2f}", inline=True)
        embed.add_field(name="👥 Squad Value", value=f"€{squad_value:,.2f}", inline=True)
        embed.add_field(name="💎 Total Club Value", value=f"€{total_value:,.2f}", inline=True)
        
        # Transfer activity
        transfers_in = [t for t in club_transfers if t['to_club'] == club_id]
        transfers_out = [t for t in club_transfers if t['from_club'] == club_id]
        
        money_spent = sum(t['amount'] for t in transfers_in)
        money_received = sum(t['amount'] for t in transfers_out)
        net_spending = money_spent - money_received
        
        embed.add_field(name="📥 Money Spent", value=f"€{money_spent:,.2f}", inline=True)
        embed.add_field(name="📤 Money Received", value=f"€{money_received:,.2f}", inline=True)
        
        net_emoji = "📈" if net_spending < 0 else "📉" if net_spending > 0 else "➡️"
        embed.add_field(name=f"{net_emoji} Net Spending", value=f"€{net_spending:,.2f}", inline=True)
        
        # Most valuable players
        if club_players:
            top_players = sorted(club_players, key=lambda x: x['value'], reverse=True)[:3]
            top_players_text = "\n".join([f"• {p['name']} - €{p['value']:,.2f}" for p in top_players])
            embed.add_field(name="🌟 Most Valuable Players", value=top_players_text, inline=False)
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2936/2936525.png")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(FinancialManagement(bot))
