"""
Visual Embeds Cog
Advanced visual embed commands with image support and beautiful designs
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class VisualEmbeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="gallery_embed", description="Create an image gallery embed with multiple images")
    @app_commands.describe(
        title="Gallery title",
        description="Gallery description",
        image1="Upload first image from album",
        image1_caption="First image caption",
        image2="Upload second image from album (optional)",
        image2_caption="Second image caption (optional)",
        image3="Upload third image from album (optional)",
        image3_caption="Third image caption (optional)"
    )
    async def gallery_embed(self, interaction: discord.Interaction, title: str, description: str = None,
                           image1: discord.Attachment = None, image1_caption: str = None,
                           image2: discord.Attachment = None, image2_caption: str = None,
                           image3: discord.Attachment = None, image3_caption: str = None):
        """Create image gallery embed"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        if not image1:
            await interaction.response.send_message("❌ At least one image is required!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🖼️ {title}",
            description=description or "*Image Gallery*",
            color=discord.Color.purple()
        )
        
        # Main image
        embed.set_image(url=image1.url)
        
        # Add image captions as fields
        if image1_caption:
            embed.add_field(name="📸 Image 1", value=image1_caption, inline=False)
        
        # Create additional embeds for other images
        embeds = [embed]
        
        if image2:
            embed2 = discord.Embed(
                title=f"🖼️ {title} - Image 2",
                description=image2_caption or "*Gallery Image 2*",
                color=discord.Color.purple()
            )
            embed2.set_image(url=image2.url)
            embeds.append(embed2)
        
        if image3:
            embed3 = discord.Embed(
                title=f"🖼️ {title} - Image 3", 
                description=image3_caption or "*Gallery Image 3*",
                color=discord.Color.purple()
            )
            embed3.set_image(url=image3.url)
            embeds.append(embed3)
        
        # Add footer to all embeds
        for i, emb in enumerate(embeds):
            emb.set_footer(text=f"Gallery {i+1}/{len(embeds)} • {interaction.guild.name}")
            emb.timestamp = datetime.now()
        
        await interaction.response.send_message(embeds=embeds)
    
    @app_commands.command(name="announcement_embed", description="Create beautiful announcement with image")
    @app_commands.describe(
        announcement_type="Type: news, update, event, or warning",
        title="Announcement title",
        message="Announcement message",
        image="Upload announcement image from album",
        ping_role="Role to ping (optional)"
    )
    async def announcement_embed(self, interaction: discord.Interaction, announcement_type: str, title: str, 
                               message: str, image: discord.Attachment = None, ping_role: str = None):
        """Create announcement embed"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Announcement styles
        styles = {
            "news": {
                "color": discord.Color.blue(),
                "emoji": "📰",
                "prefix": "NEWS"
            },
            "update": {
                "color": discord.Color.green(),
                "emoji": "🔄",
                "prefix": "UPDATE"
            },
            "event": {
                "color": discord.Color.gold(),
                "emoji": "🎉",
                "prefix": "EVENT"
            },
            "warning": {
                "color": discord.Color.red(),
                "emoji": "⚠️",
                "prefix": "WARNING"
            }
        }
        
        style = styles.get(announcement_type.lower(), styles["news"])
        
        embed = discord.Embed(
            title=f"{style['emoji']} {style['prefix']}: {title}",
            description=message,
            color=style['color']
        )
        
        if image:
            embed.set_image(url=image.url)
        
        embed.add_field(
            name="📅 Published",
            value=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            inline=True
        )
        
        embed.add_field(
            name="👤 By",
            value=interaction.user.display_name,
            inline=True
        )
        
        embed.set_footer(text=f"Official {interaction.guild.name} Announcement")
        embed.timestamp = datetime.now()
        
        # Prepare message content
        content = ""
        if ping_role:
            # Try to find the role
            role = discord.utils.get(interaction.guild.roles, name=ping_role)
            if role:
                content = f"{role.mention}"
        
        await interaction.response.send_message(content=content, embed=embed)
    
    @app_commands.command(name="match_result", description="Create football match result embed with images")
    @app_commands.describe(
        home_team="Home team name",
        away_team="Away team name",
        home_score="Home team score",
        away_score="Away team score",
        match_image="Upload match image from album",
        home_logo="Upload home team logo from album",
        away_logo="Upload away team logo from album"
    )
    async def match_result(self, interaction: discord.Interaction, home_team: str, away_team: str,
                          home_score: int, away_score: int, match_image: discord.Attachment = None,
                          home_logo: discord.Attachment = None, away_logo: discord.Attachment = None):
        """Create match result embed"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Determine result
        if home_score > away_score:
            result_color = discord.Color.green()
            result_text = f"🏆 {home_team} WINS!"
        elif away_score > home_score:
            result_color = discord.Color.red()
            result_text = f"🏆 {away_team} WINS!"
        else:
            result_color = discord.Color.orange()
            result_text = "⚖️ DRAW!"
        
        embed = discord.Embed(
            title="⚽ MATCH RESULT",
            description=result_text,
            color=result_color
        )
        
        if match_image:
            embed.set_image(url=match_image.url)
        
        # Score display
        embed.add_field(
            name="📊 FINAL SCORE",
            value=f"**{home_team} {home_score} - {away_score} {away_team}**",
            inline=False
        )
        
        # Team info
        embed.add_field(
            name=f"🏠 {home_team}",
            value=f"⚽ Goals: {home_score}\n🏟️ Home Advantage",
            inline=True
        )
        
        embed.add_field(
            name=f"✈️ {away_team}",
            value=f"⚽ Goals: {away_score}\n🚌 Away Team",
            inline=True
        )
        
        # Match stats
        embed.add_field(
            name="📈 Match Stats",
            value=f"🎯 Total Goals: {home_score + away_score}\n⏱️ Match Time: 90 minutes",
            inline=True
        )
        
        # Add team logos as thumbnails if provided
        if home_logo:
            embed.set_thumbnail(url=home_logo.url)
        
        embed.set_footer(text=f"Match played in {interaction.guild.name} League")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stats_infographic", description="Create beautiful statistics infographic")
    @app_commands.describe(
        stat_type="Type: player, club, or league",
        subject="Subject name (player/club)",
        background_image="Upload background image from album",
        stat_color="Color theme"
    )
    async def stats_infographic(self, interaction: discord.Interaction, stat_type: str, subject: str = None,
                              background_image: discord.Attachment = None, stat_color: str = "blue"):
        """Create stats infographic"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Color mapping
        color_map = {
            'blue': discord.Color.blue(),
            'green': discord.Color.green(),
            'red': discord.Color.red(),
            'purple': discord.Color.purple(),
            'gold': discord.Color.gold()
        }
        embed_color = color_map.get(stat_color.lower(), discord.Color.blue())
        
        if stat_type.lower() == "player" and subject:
            player_id = f"{interaction.guild.id}_{subject.lower().replace(' ', '_')}"
            player_data = self.db.get_player(player_id)
            
            if not player_data:
                await interaction.response.send_message(f"❌ Player '{subject}' not found!", ephemeral=True)
                return
            
            # Get transfers
            transfers = self.db.get_transfers()
            player_transfers = [t for t in transfers if t['player_id'] == player_id]
            
            embed = discord.Embed(
                title=f"📊 {player_data['name']} - Player Statistics",
                description="*Comprehensive Player Analysis*",
                color=embed_color
            )
            
            if background_image:
                embed.set_image(url=background_image.url)
            
            # Basic stats
            embed.add_field(
                name="💎 Market Value",
                value=f"€{player_data['value']:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="🎂 Age",
                value=f"{player_data.get('age', 'N/A')} years",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Position",
                value=player_data.get('position', 'N/A'),
                inline=True
            )
            
            # Transfer stats
            embed.add_field(
                name="🔄 Career Transfers",
                value=str(len(player_transfers)),
                inline=True
            )
            
            if player_transfers:
                total_transfer_value = sum(t['amount'] for t in player_transfers)
                embed.add_field(
                    name="💰 Total Transfer Value",
                    value=f"€{total_transfer_value:,.0f}",
                    inline=True
                )
            
            # Club info
            club_name = "Free Agent"
            if player_data.get('club_id'):
                club = self.db.get_club(player_data['club_id'])
                if club:
                    club_name = club['name']
            
            embed.add_field(
                name="⚽ Current Club",
                value=club_name,
                inline=True
            )
            
        elif stat_type.lower() == "club" and subject:
            club_id = f"{interaction.guild.id}_{subject.lower().replace(' ', '_')}"
            club_data = self.db.get_club(club_id)
            
            if not club_data:
                await interaction.response.send_message(f"❌ Club '{subject}' not found!", ephemeral=True)
                return
            
            players = self.db.get_players()
            club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
            
            embed = discord.Embed(
                title=f"🏟️ {club_data['name']} - Club Statistics",
                description="*Complete Club Analysis*",
                color=embed_color
            )
            
            if background_image:
                embed.set_image(url=background_image.url)
            
            # Financial stats
            total_player_value = sum(p['value'] for p in club_players)
            
            embed.add_field(
                name="💰 Available Budget",
                value=f"€{club_data['budget']:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="💎 Squad Value",
                value=f"€{total_player_value:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="🏦 Total Worth",
                value=f"€{(club_data['budget'] + total_player_value):,.0f}",
                inline=True
            )
            
            # Squad stats
            embed.add_field(
                name="👥 Squad Size",
                value=str(len(club_players)),
                inline=True
            )
            
            if club_players:
                avg_value = total_player_value / len(club_players)
                embed.add_field(
                    name="📊 Average Player Value",
                    value=f"€{avg_value:,.0f}",
                    inline=True
                )
                
                most_valuable = max(club_players, key=lambda x: x['value'])
                embed.add_field(
                    name="⭐ Most Valuable Player",
                    value=f"{most_valuable['name']}\n€{most_valuable['value']:,.0f}",
                    inline=True
                )
        
        else:
            # League stats
            clubs = self.db.get_clubs()
            players = self.db.get_players()
            transfers = self.db.get_transfers()
            
            guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
            guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
            guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
            
            embed = discord.Embed(
                title=f"🏆 {interaction.guild.name} League Statistics",
                description="*Complete League Overview*",
                color=embed_color
            )
            
            if background_image:
                embed.set_image(url=background_image.url)
            
            # Basic counts
            embed.add_field(
                name="🏟️ Total Clubs",
                value=str(len(guild_clubs)),
                inline=True
            )
            
            embed.add_field(
                name="👥 Total Players",
                value=str(len(guild_players)),
                inline=True
            )
            
            embed.add_field(
                name="🔄 Total Transfers",
                value=str(len(guild_transfers)),
                inline=True
            )
            
            # Financial overview
            total_budgets = sum(c['budget'] for c in guild_clubs.values())
            total_player_values = sum(p['value'] for p in guild_players.values())
            
            embed.add_field(
                name="💰 Total Club Budgets",
                value=f"€{total_budgets:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="💎 Total Player Values",
                value=f"€{total_player_values:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="🌟 League Total Value",
                value=f"€{(total_budgets + total_player_values):,.0f}",
                inline=True
            )
        
        embed.set_footer(text=f"Statistics generated • {interaction.guild.name}")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="transfer_card", description="Create transfer announcement card with images")
    @app_commands.describe(
        player="Player name",
        from_club="Previous club (or 'Free Agent')",
        to_club="New club",
        transfer_fee="Transfer fee in Euros",
        player_image="Upload player image from album",
        announcement_style="Style: official, breaking, or celebration"
    )
    async def transfer_card(self, interaction: discord.Interaction, player: str, from_club: str, 
                           to_club: str, transfer_fee: float, player_image: discord.Attachment = None, 
                           announcement_style: str = "official"):
        """Create transfer announcement card"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Styles
        styles = {
            "official": {
                "color": discord.Color.blue(),
                "emoji": "📋",
                "prefix": "OFFICIAL"
            },
            "breaking": {
                "color": discord.Color.red(),
                "emoji": "🚨",
                "prefix": "BREAKING"
            },
            "celebration": {
                "color": discord.Color.gold(),
                "emoji": "🎉",
                "prefix": "COMPLETED"
            }
        }
        
        style = styles.get(announcement_style.lower(), styles["official"])
        
        embed = discord.Embed(
            title=f"{style['emoji']} {style['prefix']} TRANSFER",
            description=f"**{player}** has officially joined **{to_club}**!",
            color=style['color']
        )
        
        if player_image:
            embed.set_image(url=player_image.url)
        
        # Transfer details
        embed.add_field(
            name="👤 Player",
            value=player,
            inline=True
        )
        
        embed.add_field(
            name="📤 From",
            value=from_club,
            inline=True
        )
        
        embed.add_field(
            name="📥 To",
            value=to_club,
            inline=True
        )
        
        embed.add_field(
            name="💰 Transfer Fee",
            value=f"€{transfer_fee:,.0f}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Date",
            value=datetime.now().strftime("%B %d, %Y"),
            inline=True
        )
        
        embed.add_field(
            name="✅ Status",
            value="Completed ✔️",
            inline=True
        )
        
        embed.set_footer(text=f"Transfer completed in {interaction.guild.name} League")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(VisualEmbeds(bot))