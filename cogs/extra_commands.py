"""
Extra Commands Cog
Additional useful commands and price management features
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import random
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class ExtraCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="bulk_price_update", description="Update multiple players' values at once")
    @app_commands.describe(
        percentage="Percentage change (-50 to 200)",
        club="Club name (optional, affects all players if not specified)",
        position="Position filter (optional: GK, DEF, MID, FWD)"
    )
    async def bulk_price_update(self, interaction: discord.Interaction, percentage: float, club: str = None, position: str = None):
        """Bulk update player values"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if percentage < -50 or percentage > 200:
            await interaction.response.send_message("❌ Percentage must be between -50% and +200%!", ephemeral=True)
            return
        
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        # Filter players
        filtered_players = {}
        for player_id, player_data in guild_players.items():
            include = True
            
            # Club filter
            if club:
                club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
                if player_data.get('club_id') != club_id:
                    include = False
            
            # Position filter
            if position and include:
                if player_data.get('position', '').upper() != position.upper():
                    include = False
            
            if include:
                filtered_players[player_id] = player_data
        
        if not filtered_players:
            await interaction.response.send_message("❌ No players found matching the criteria!", ephemeral=True)
            return
        
        # Update values
        multiplier = 1 + (percentage / 100)
        updated_count = 0
        total_old_value = 0
        total_new_value = 0
        
        for player_id, player_data in filtered_players.items():
            old_value = player_data['value']
            new_value = round(old_value * multiplier, 2)
            
            if self.db.update_player_value(player_id, new_value):
                updated_count += 1
                total_old_value += old_value
                total_new_value += new_value
        
        embed = discord.Embed(
            title="📈 Bulk Price Update Completed",
            color=discord.Color.green(),
            description=f"Updated {updated_count} player(s) by {percentage:+.1f}%"
        )
        
        if club:
            embed.add_field(name="🏟️ Club", value=club, inline=True)
        if position:
            embed.add_field(name="🎯 Position", value=position.upper(), inline=True)
        
        embed.add_field(name="📊 Total Old Value", value=f"€{total_old_value:,.2f}", inline=True)
        embed.add_field(name="📊 Total New Value", value=f"€{total_new_value:,.2f}", inline=True)
        
        value_change = total_new_value - total_old_value
        change_emoji = "📈" if value_change > 0 else "📉" if value_change < 0 else "➡️"
        embed.add_field(name="💰 Value Change", value=f"{change_emoji} €{value_change:,.2f}", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="budget_multiplier", description="Multiply all club budgets by a factor")
    @app_commands.describe(multiplier="Budget multiplier (0.1 to 10.0)")
    async def budget_multiplier(self, interaction: discord.Interaction, multiplier: float):
        """Multiply all budgets"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if multiplier < 0.1 or multiplier > 10.0:
            await interaction.response.send_message("❌ Multiplier must be between 0.1 and 10.0!", ephemeral=True)
            return
        
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_clubs:
            await interaction.response.send_message("❌ No clubs found!", ephemeral=True)
            return
        
        updated_clubs = []
        total_old_budget = 0
        total_new_budget = 0
        
        for club_id, club_data in guild_clubs.items():
            old_budget = club_data['budget']
            new_budget = round(old_budget * multiplier, 2)
            
            if self.db.update_club_budget(club_id, new_budget):
                updated_clubs.append((club_data['name'], old_budget, new_budget))
                total_old_budget += old_budget
                total_new_budget += new_budget
        
        embed = discord.Embed(
            title="💰 Budget Multiplier Applied",
            color=discord.Color.blue(),
            description=f"Applied {multiplier}x multiplier to {len(updated_clubs)} club(s)"
        )
        
        embed.add_field(name="📊 Total Old Budget", value=f"€{total_old_budget:,.2f}", inline=True)
        embed.add_field(name="📊 Total New Budget", value=f"€{total_new_budget:,.2f}", inline=True)
        
        budget_change = total_new_budget - total_old_budget
        change_emoji = "📈" if budget_change > 0 else "📉" if budget_change < 0 else "➡️"
        embed.add_field(name="💰 Budget Change", value=f"{change_emoji} €{budget_change:,.2f}", inline=True)
        
        # Show individual changes
        changes_text = ""
        for name, old_budget, new_budget in updated_clubs[:8]:  # Show first 8
            changes_text += f"• {name}: €{old_budget:,.0f} → €{new_budget:,.0f}\n"
        
        if len(updated_clubs) > 8:
            changes_text += f"... and {len(updated_clubs) - 8} more clubs"
        
        embed.add_field(name="🔄 Changes", value=changes_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="random_player_value", description="Randomize player values within a range")
    @app_commands.describe(
        min_value="Minimum value in Euros",
        max_value="Maximum value in Euros",
        club="Club name (optional)"
    )
    async def random_player_value(self, interaction: discord.Interaction, min_value: float, max_value: float, club: str = None):
        """Randomize player values"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if min_value >= max_value or min_value < 0:
            await interaction.response.send_message("❌ Invalid value range!", ephemeral=True)
            return
        
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        # Filter by club if specified
        if club:
            club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
            if not self.db.get_club(club_id):
                await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
                return
            guild_players = {k: v for k, v in guild_players.items() if v.get('club_id') == club_id}
        
        if not guild_players:
            await interaction.response.send_message("❌ No players found!", ephemeral=True)
            return
        
        updated_count = 0
        for player_id in guild_players.keys():
            new_value = round(random.uniform(min_value, max_value), 2)
            if self.db.update_player_value(player_id, new_value):
                updated_count += 1
        
        embed = discord.Embed(
            title="🎲 Player Values Randomized",
            color=discord.Color.purple(),
            description=f"Randomized {updated_count} player values"
        )
        
        embed.add_field(name="💰 Value Range", value=f"€{min_value:,.2f} - €{max_value:,.2f}", inline=True)
        if club:
            embed.add_field(name="🏟️ Club", value=club, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="salary_cap", description="Set a salary cap and adjust overvalued players")
    @app_commands.describe(
        cap="Maximum player value allowed",
        action="What to do with overvalued players: 'cap' or 'release'"
    )
    async def salary_cap(self, interaction: discord.Interaction, cap: float, action: str = "cap"):
        """Implement salary cap"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if action.lower() not in ["cap", "release"]:
            await interaction.response.send_message("❌ Action must be 'cap' or 'release'!", ephemeral=True)
            return
        
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        overvalued_players = {k: v for k, v in guild_players.items() if v['value'] > cap}
        
        if not overvalued_players:
            await interaction.response.send_message(f"✅ All players are already under the salary cap of €{cap:,.2f}!", ephemeral=True)
            return
        
        processed = 0
        capped = 0
        released = 0
        
        for player_id, player_data in overvalued_players.items():
            if action.lower() == "cap":
                if self.db.update_player_value(player_id, cap):
                    capped += 1
                    processed += 1
            else:  # release
                # Transfer to free agency
                if player_data.get('club_id'):
                    if self.db.add_transfer(player_id, player_data['club_id'], None, 0):
                        released += 1
                        processed += 1
        
        embed = discord.Embed(
            title="🧢 Salary Cap Applied",
            color=discord.Color.orange(),
            description=f"Processed {processed} overvalued player(s)"
        )
        
        embed.add_field(name="💰 Salary Cap", value=f"€{cap:,.2f}", inline=True)
        embed.add_field(name="👥 Affected Players", value=str(len(overvalued_players)), inline=True)
        embed.add_field(name="🔧 Action", value=action.capitalize(), inline=True)
        
        if action.lower() == "cap":
            embed.add_field(name="📉 Players Capped", value=str(capped), inline=True)
        else:
            embed.add_field(name="🆓 Players Released", value=str(released), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="market_crash", description="Simulate a market crash with random value decreases")
    @app_commands.describe(
        min_decrease="Minimum decrease percentage (5-50)",
        max_decrease="Maximum decrease percentage (10-80)"
    )
    async def market_crash(self, interaction: discord.Interaction, min_decrease: float = 10.0, max_decrease: float = 40.0):
        """Simulate market crash"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if min_decrease < 5 or max_decrease > 80 or min_decrease >= max_decrease:
            await interaction.response.send_message("❌ Invalid decrease range! Min: 5-50%, Max: 10-80%", ephemeral=True)
            return
        
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("❌ No players found!", ephemeral=True)
            return
        
        total_old_value = 0
        total_new_value = 0
        updated_count = 0
        
        for player_id, player_data in guild_players.items():
            old_value = player_data['value']
            decrease_percent = random.uniform(min_decrease, max_decrease)
            new_value = round(old_value * (1 - decrease_percent / 100), 2)
            
            if self.db.update_player_value(player_id, new_value):
                total_old_value += old_value
                total_new_value += new_value
                updated_count += 1
        
        total_loss = total_old_value - total_new_value
        avg_decrease = ((total_old_value - total_new_value) / total_old_value) * 100
        
        embed = discord.Embed(
            title="💥 Market Crash Simulated!",
            color=discord.Color.red(),
            description=f"The market has crashed! All player values decreased."
        )
        
        embed.add_field(name="📉 Players Affected", value=str(updated_count), inline=True)
        embed.add_field(name="📊 Average Decrease", value=f"{avg_decrease:.1f}%", inline=True)
        embed.add_field(name="💸 Total Value Lost", value=f"€{total_loss:,.2f}", inline=True)
        
        embed.add_field(name="📊 Before Crash", value=f"€{total_old_value:,.2f}", inline=True)
        embed.add_field(name="📊 After Crash", value=f"€{total_new_value:,.2f}", inline=True)
        embed.add_field(name="📈 Recovery Needed", value=f"{((total_old_value / total_new_value - 1) * 100):.1f}%", inline=True)
        
        embed.set_footer(text="💡 Use /market_boom to simulate a recovery!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="market_boom", description="Simulate a market boom with value increases")
    @app_commands.describe(
        min_increase="Minimum increase percentage (5-100)",
        max_increase="Maximum increase percentage (20-200)"
    )
    async def market_boom(self, interaction: discord.Interaction, min_increase: float = 15.0, max_increase: float = 60.0):
        """Simulate market boom"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if min_increase < 5 or max_increase > 200 or min_increase >= max_increase:
            await interaction.response.send_message("❌ Invalid increase range! Min: 5-100%, Max: 20-200%", ephemeral=True)
            return
        
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("❌ No players found!", ephemeral=True)
            return
        
        total_old_value = 0
        total_new_value = 0
        updated_count = 0
        
        for player_id, player_data in guild_players.items():
            old_value = player_data['value']
            increase_percent = random.uniform(min_increase, max_increase)
            new_value = round(old_value * (1 + increase_percent / 100), 2)
            
            if self.db.update_player_value(player_id, new_value):
                total_old_value += old_value
                total_new_value += new_value
                updated_count += 1
        
        total_gain = total_new_value - total_old_value
        avg_increase = ((total_new_value - total_old_value) / total_old_value) * 100
        
        embed = discord.Embed(
            title="🚀 Market Boom!",
            color=discord.Color.gold(),
            description=f"The market is booming! All player values increased."
        )
        
        embed.add_field(name="📈 Players Affected", value=str(updated_count), inline=True)
        embed.add_field(name="📊 Average Increase", value=f"{avg_increase:.1f}%", inline=True)
        embed.add_field(name="💰 Total Value Gained", value=f"€{total_gain:,.2f}", inline=True)
        
        embed.add_field(name="📊 Before Boom", value=f"€{total_old_value:,.2f}", inline=True)
        embed.add_field(name="📊 After Boom", value=f"€{total_new_value:,.2f}", inline=True)
        embed.add_field(name="🎯 Growth Rate", value=f"{((total_new_value / total_old_value - 1) * 100):.1f}%", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="inflation_adjustment", description="Apply inflation to all values and budgets")
    @app_commands.describe(rate="Inflation rate percentage (1-20)")
    async def inflation_adjustment(self, interaction: discord.Interaction, rate: float):
        """Apply inflation adjustment"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if rate < 1 or rate > 20:
            await interaction.response.send_message("❌ Inflation rate must be between 1% and 20%!", ephemeral=True)
            return
        
        # Update player values
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        # Update club budgets
        clubs = self.db.get_clubs()
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        
        multiplier = 1 + (rate / 100)
        
        player_updates = 0
        club_updates = 0
        
        # Update players
        for player_id, player_data in guild_players.items():
            new_value = round(player_data['value'] * multiplier, 2)
            if self.db.update_player_value(player_id, new_value):
                player_updates += 1
        
        # Update clubs
        for club_id, club_data in guild_clubs.items():
            new_budget = round(club_data['budget'] * multiplier, 2)
            if self.db.update_club_budget(club_id, new_budget):
                club_updates += 1
        
        embed = discord.Embed(
            title="📊 Inflation Adjustment Applied",
            color=discord.Color.blue(),
            description=f"Applied {rate}% inflation to all values and budgets"
        )
        
        embed.add_field(name="👥 Players Updated", value=str(player_updates), inline=True)
        embed.add_field(name="🏟️ Clubs Updated", value=str(club_updates), inline=True)
        embed.add_field(name="📈 Rate Applied", value=f"{rate}%", inline=True)
        
        embed.set_footer(text="All player values and club budgets have been adjusted for inflation.")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ExtraCommands(bot))