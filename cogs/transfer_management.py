"""
Transfer Management Cog
Handles player transfers between clubs
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class TransferManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="transfer_player", description="Transfer a player between clubs")
    @app_commands.describe(
        player="Name of the player",
        to_club="Destination club",
        amount="Transfer fee in Euros"
    )
    async def transfer_player(self, interaction: discord.Interaction, player: str, to_club: str, amount: float):
        """Transfer a player to another club"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Get player and clubs
        player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
        to_club_id = f"{interaction.guild.id}_{to_club.lower().replace(' ', '_')}"
        
        player_data = self.db.get_player(player_id)
        to_club_data = self.db.get_club(to_club_id)
        
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{player}' not found!", ephemeral=True)
            return
        
        if not to_club_data:
            await interaction.response.send_message(f"❌ Club '{to_club}' not found!", ephemeral=True)
            return
        
        # Check if destination club has enough budget
        if to_club_data['budget'] < amount:
            await interaction.response.send_message(
                f"❌ {to_club} doesn't have enough budget! Available: €{to_club_data['budget']:,.2f}, Required: €{amount:,.2f}",
                ephemeral=True
            )
            return
        
        # Get source club info
        from_club_id = player_data.get('club_id')
        from_club_name = "Free Agency"
        
        if from_club_id:
            from_club_data = self.db.get_club(from_club_id)
            if from_club_data:
                from_club_name = from_club_data['name']
        
        # Perform transfer
        if self.db.add_transfer(player_id, from_club_id, to_club_id, amount):
            embed = discord.Embed(
                title="🔄 Transfer Completed!",
                color=discord.Color.green(),
                description=f"**{player_data['name']}** has been transferred!"
            )
            
            embed.add_field(name="👤 Player", value=player_data['name'], inline=True)
            embed.add_field(name="📤 From", value=from_club_name, inline=True)
            embed.add_field(name="📥 To", value=to_club, inline=True)
            embed.add_field(name="💰 Transfer Fee", value=f"€{amount:,.2f}", inline=True)
            embed.add_field(name="💎 Player Value", value=f"€{player_data['value']:,.2f}", inline=True)
            
            # Calculate profit/loss for selling club
            if from_club_id:
                profit_loss = amount - player_data['value']
                if profit_loss > 0:
                    embed.add_field(name="📈 Profit", value=f"€{profit_loss:,.2f}", inline=True)
                elif profit_loss < 0:
                    embed.add_field(name="📉 Loss", value=f"€{abs(profit_loss):,.2f}", inline=True)
                else:
                    embed.add_field(name="➡️ Break Even", value="€0.00", inline=True)
            
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2936/2936719.png")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Transfer failed. Please try again.", ephemeral=True)
    
    @app_commands.command(name="release_player", description="Release a player from their club")
    @app_commands.describe(player="Name of the player to release")
    async def release_player(self, interaction: discord.Interaction, player: str):
        """Release a player to free agency"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
        player_data = self.db.get_player(player_id)
        
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{player}' not found!", ephemeral=True)
            return
        
        if not player_data.get('club_id'):
            await interaction.response.send_message(f"❌ {player} is already a free agent!", ephemeral=True)
            return
        
        # Get club info
        club_data = self.db.get_club(player_data['club_id'])
        club_name = club_data['name'] if club_data else "Unknown Club"
        
        # Release player (transfer to free agency)
        if self.db.add_transfer(player_id, player_data['club_id'], None, 0):
            embed = discord.Embed(
                title="🆓 Player Released",
                color=discord.Color.orange(),
                description=f"**{player_data['name']}** has been released to free agency!"
            )
            
            embed.add_field(name="👤 Player", value=player_data['name'], inline=True)
            embed.add_field(name="📤 Released From", value=club_name, inline=True)
            embed.add_field(name="💎 Market Value", value=f"€{player_data['value']:,.2f}", inline=True)
            
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1828/1828843.png")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to release player. Please try again.", ephemeral=True)
    
    @app_commands.command(name="transfer_history", description="View transfer history")
    @app_commands.describe(
        player="Player name (optional)",
        club="Club name (optional)"
    )
    async def transfer_history(self, interaction: discord.Interaction, player: str = None, club: str = None):
        """View transfer history"""
        transfers = self.db.get_transfers()
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        if not guild_transfers:
            await interaction.response.send_message("📋 No transfers found.", ephemeral=True)
            return
        
        # Filter transfers
        filtered_transfers = guild_transfers
        
        if player:
            player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
            filtered_transfers = [t for t in filtered_transfers if t['player_id'] == player_id]
        
        if club:
            club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
            filtered_transfers = [t for t in filtered_transfers if t['from_club'] == club_id or t['to_club'] == club_id]
        
        if not filtered_transfers:
            await interaction.response.send_message("📋 No matching transfers found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔄 Transfer History",
            color=discord.Color.blue(),
            description="Recent player transfers"
        )
        
        # Sort by date (most recent first)
        sorted_transfers = sorted(filtered_transfers, key=lambda x: x['date'], reverse=True)
        
        for i, transfer in enumerate(sorted_transfers[:10]):  # Show last 10 transfers
            # Get player name
            player_data = self.db.get_player(transfer['player_id'])
            player_name = player_data['name'] if player_data else "Unknown Player"
            
            # Get club names
            from_club_name = "Free Agency"
            to_club_name = "Free Agency"
            
            if transfer['from_club']:
                from_club = self.db.get_club(transfer['from_club'])
                if from_club:
                    from_club_name = from_club['name']
            
            if transfer['to_club']:
                to_club = self.db.get_club(transfer['to_club'])
                if to_club:
                    to_club_name = to_club['name']
            
            embed.add_field(
                name=f"{i+1}. {player_name}",
                value=f"📤 From: {from_club_name}\n📥 To: {to_club_name}\n💰 Fee: €{transfer['amount']:,.2f}",
                inline=True
            )
        
        if len(sorted_transfers) > 10:
            embed.set_footer(text=f"Showing 10 of {len(sorted_transfers)} transfers")
        else:
            embed.set_footer(text=f"Total transfers: {len(sorted_transfers)}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="market_activity", description="View recent market activity")
    async def market_activity(self, interaction: discord.Interaction):
        """Show recent market activity with statistics"""
        transfers = self.db.get_transfers()
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        if not guild_transfers:
            await interaction.response.send_message("📋 No market activity found.", ephemeral=True)
            return
        
        # Calculate statistics
        total_transfers = len(guild_transfers)
        total_spent = sum(t['amount'] for t in guild_transfers)
        average_fee = total_spent / total_transfers if total_transfers > 0 else 0
        
        # Most expensive transfer
        most_expensive = max(guild_transfers, key=lambda x: x['amount']) if guild_transfers else None
        
        embed = discord.Embed(
            title="📊 Transfer Market Activity",
            color=discord.Color.purple(),
            description="Market statistics and recent activity"
        )
        
        embed.add_field(name="🔄 Total Transfers", value=str(total_transfers), inline=True)
        embed.add_field(name="💰 Total Spent", value=f"€{total_spent:,.2f}", inline=True)
        embed.add_field(name="📈 Average Fee", value=f"€{average_fee:,.2f}", inline=True)
        
        if most_expensive:
            player_data = self.db.get_player(most_expensive['player_id'])
            player_name = player_data['name'] if player_data else "Unknown"
            embed.add_field(
                name="💎 Most Expensive Transfer",
                value=f"{player_name} - €{most_expensive['amount']:,.2f}",
                inline=False
            )
        
        # Recent transfers
        recent_transfers = sorted(guild_transfers, key=lambda x: x['date'], reverse=True)[:5]
        if recent_transfers:
            recent_text = ""
            for transfer in recent_transfers:
                player_data = self.db.get_player(transfer['player_id'])
                player_name = player_data['name'] if player_data else "Unknown"
                recent_text += f"• {player_name} - €{transfer['amount']:,.2f}\n"
            
            embed.add_field(name="🆕 Recent Transfers", value=recent_text, inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TransferManagement(bot))
