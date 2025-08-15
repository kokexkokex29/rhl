"""
Utility Commands Cog
Additional utility commands for enhanced bot functionality
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
from datetime import datetime, timedelta
from utils.permissions import check_admin

logger = logging.getLogger(__name__)

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="duplicate_player", description="Create a duplicate of an existing player")
    @app_commands.describe(
        original="Original player name",
        new_name="New player name",
        club="Club for the new player (optional)"
    )
    async def duplicate_player(self, interaction: discord.Interaction, original: str, new_name: str, club: str = None):
        """Duplicate an existing player"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        original_id = f"{interaction.guild.id}_{original.lower().replace(' ', '_')}"
        new_id = f"{interaction.guild.id}_{new_name.lower().replace(' ', '_')}"
        
        original_player = self.db.get_player(original_id)
        if not original_player:
            await interaction.response.send_message(f"❌ Player '{original}' not found!", ephemeral=True)
            return
        
        if self.db.get_player(new_id):
            await interaction.response.send_message(f"❌ Player '{new_name}' already exists!", ephemeral=True)
            return
        
        # Get club ID if specified
        club_id = None
        if club:
            club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
            if not self.db.get_club(club_id):
                await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
                return
        
        # Create duplicate
        if self.db.add_player(new_id, new_name, original_player['value'], club_id, 
                             original_player.get('position', ''), original_player.get('age', 0)):
            embed = discord.Embed(
                title="👥 Player Duplicated",
                color=discord.Color.green(),
                description=f"Created **{new_name}** as duplicate of **{original}**"
            )
            
            embed.add_field(name="💎 Value", value=f"€{original_player['value']:,.2f}", inline=True)
            if original_player.get('position'):
                embed.add_field(name="🎯 Position", value=original_player['position'], inline=True)
            if original_player.get('age', 0) > 0:
                embed.add_field(name="🎂 Age", value=f"{original_player['age']} years", inline=True)
            
            club_name = "Free Agent"
            if club_id:
                club_data = self.db.get_club(club_id)
                if club_data:
                    club_name = club_data['name']
            embed.add_field(name="⚽ Club", value=club_name, inline=True)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to duplicate player.", ephemeral=True)
    
    @app_commands.command(name="player_age_groups", description="Show players grouped by age ranges")
    async def player_age_groups(self, interaction: discord.Interaction):
        """Show age group distribution"""
        players = self.db.get_players()
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        
        if not guild_players:
            await interaction.response.send_message("📋 No players found.", ephemeral=True)
            return
        
        # Age groups
        age_groups = {
            "Youth (16-20)": [],
            "Young (21-25)": [],
            "Prime (26-30)": [],
            "Veteran (31-35)": [],
            "Legend (36+)": [],
            "Unknown Age": []
        }
        
        for player_data in guild_players.values():
            age = player_data.get('age', 0)
            if age == 0:
                age_groups["Unknown Age"].append(player_data)
            elif age <= 20:
                age_groups["Youth (16-20)"].append(player_data)
            elif age <= 25:
                age_groups["Young (21-25)"].append(player_data)
            elif age <= 30:
                age_groups["Prime (26-30)"].append(player_data)
            elif age <= 35:
                age_groups["Veteran (31-35)"].append(player_data)
            else:
                age_groups["Legend (36+)"].append(player_data)
        
        embed = discord.Embed(
            title="🎂 Player Age Distribution",
            color=discord.Color.blue(),
            description="Players grouped by age ranges"
        )
        
        for group_name, players_list in age_groups.items():
            if players_list:
                avg_value = sum(p['value'] for p in players_list) / len(players_list)
                most_valuable = max(players_list, key=lambda x: x['value'])
                
                embed.add_field(
                    name=f"{group_name} ({len(players_list)})",
                    value=f"💎 Avg Value: €{avg_value:,.0f}\n⭐ Top: {most_valuable['name']} (€{most_valuable['value']:,.0f})",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="import_players_csv", description="Import players from CSV-like format")
    @app_commands.describe(
        data="Players in format: Name,Value,Position,Age,Club (one per line)"
    )
    async def import_players_csv(self, interaction: discord.Interaction, data: str):
        """Import players from CSV format"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        lines = data.strip().split('\n')
        imported = 0
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) < 2:
                    errors.append(f"Line {line_num}: Not enough data")
                    continue
                
                name = parts[0]
                value = float(parts[1])
                position = parts[2] if len(parts) > 2 and parts[2] else ""
                age = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
                club_name = parts[4] if len(parts) > 4 and parts[4] else None
                
                # Validate
                if not name:
                    errors.append(f"Line {line_num}: Empty name")
                    continue
                
                player_id = f"{interaction.guild.id}_{name.lower().replace(' ', '_')}"
                if self.db.get_player(player_id):
                    errors.append(f"Line {line_num}: Player '{name}' already exists")
                    continue
                
                club_id = None
                if club_name:
                    club_id = f"{interaction.guild.id}_{club_name.lower().replace(' ', '_')}"
                    if not self.db.get_club(club_id):
                        errors.append(f"Line {line_num}: Club '{club_name}' not found")
                        continue
                
                # Import player
                if self.db.add_player(player_id, name, value, club_id, position.upper(), age):
                    imported += 1
                else:
                    errors.append(f"Line {line_num}: Failed to import '{name}'")
                    
            except ValueError as e:
                errors.append(f"Line {line_num}: Invalid data format")
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
        
        embed = discord.Embed(
            title="📥 Player Import Results",
            color=discord.Color.green() if imported > 0 else discord.Color.red(),
            description=f"Processed {len(lines)} line(s)"
        )
        
        embed.add_field(name="✅ Successfully Imported", value=str(imported), inline=True)
        embed.add_field(name="❌ Errors", value=str(len(errors)), inline=True)
        
        if errors and len(errors) <= 10:
            embed.add_field(name="Error Details", value="\n".join(errors), inline=False)
        elif errors:
            embed.add_field(name="Error Details", value=f"{len(errors)} errors occurred. First few:\n" + "\n".join(errors[:5]), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="export_data", description="Export all data in readable format")
    async def export_data(self, interaction: discord.Interaction):
        """Export all data"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        clubs = self.db.get_clubs()
        players = self.db.get_players()
        transfers = self.db.get_transfers()
        
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        # Format data
        export_text = f"# Football Club Data Export - {interaction.guild.name}\n"
        export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Clubs
        export_text += "## CLUBS\n"
        for club_id, club_data in guild_clubs.items():
            export_text += f"- {club_data['name']}: €{club_data['budget']:,.2f}\n"
        
        # Players
        export_text += "\n## PLAYERS\n"
        for player_id, player_data in guild_players.items():
            club_name = "Free Agent"
            if player_data.get('club_id') and player_data['club_id'] in guild_clubs:
                club_name = guild_clubs[player_data['club_id']]['name']
            
            pos = player_data.get('position', 'N/A')
            age = player_data.get('age', 0)
            age_str = f" ({age}yo)" if age > 0 else ""
            
            export_text += f"- {player_data['name']}{age_str} [{pos}]: €{player_data['value']:,.2f} - {club_name}\n"
        
        # Transfers
        export_text += f"\n## TRANSFERS ({len(guild_transfers)})\n"
        for transfer in guild_transfers[-20:]:  # Last 20 transfers
            player_name = "Unknown"
            if transfer['player_id'] in guild_players:
                player_name = guild_players[transfer['player_id']]['name']
            
            from_club = "Free Agency"
            if transfer.get('from_club') and transfer['from_club'] in guild_clubs:
                from_club = guild_clubs[transfer['from_club']]['name']
            
            to_club = "Free Agency"
            if transfer.get('to_club') and transfer['to_club'] in guild_clubs:
                to_club = guild_clubs[transfer['to_club']]['name']
            
            export_text += f"- {player_name}: {from_club} → {to_club} (€{transfer['amount']:,.2f})\n"
        
        # Statistics
        total_player_value = sum(p['value'] for p in guild_players.values())
        total_club_budget = sum(c['budget'] for c in guild_clubs.values())
        
        export_text += f"\n## STATISTICS\n"
        export_text += f"- Total Clubs: {len(guild_clubs)}\n"
        export_text += f"- Total Players: {len(guild_players)}\n"
        export_text += f"- Total Player Value: €{total_player_value:,.2f}\n"
        export_text += f"- Total Club Budgets: €{total_club_budget:,.2f}\n"
        export_text += f"- Total Transfers: {len(guild_transfers)}\n"
        
        # Send as file if too long, otherwise as message
        if len(export_text) > 1900:
            # Create file
            file_content = export_text.encode('utf-8')
            file = discord.File(fp=discord.io.BytesIO(file_content), 
                              filename=f"football_data_export_{interaction.guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            embed = discord.Embed(
                title="📤 Data Export Complete",
                color=discord.Color.blue(),
                description="Export file generated successfully!"
            )
            
            await interaction.response.send_message(embed=embed, file=file)
        else:
            embed = discord.Embed(
                title="📤 Data Export",
                color=discord.Color.blue(),
                description=f"```\n{export_text}\n```"
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quick_setup", description="Quick setup with sample clubs and players")
    @app_commands.describe(
        theme="Setup theme: 'premier_league', 'la_liga', 'serie_a', or 'custom'"
    )
    async def quick_setup(self, interaction: discord.Interaction, theme: str = "premier_league"):
        """Quick setup with sample data"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        themes = {
            "premier_league": {
                "clubs": [
                    ("Manchester City", 300000000),
                    ("Arsenal", 250000000),
                    ("Liverpool", 280000000),
                    ("Chelsea", 200000000)
                ],
                "players": [
                    ("Erling Haaland", 150000000, "FWD", 24, "Manchester City"),
                    ("Mohamed Salah", 80000000, "FWD", 32, "Liverpool"),
                    ("Bukayo Saka", 120000000, "MID", 23, "Arsenal"),
                    ("Cole Palmer", 90000000, "MID", 22, "Chelsea")
                ]
            },
            "la_liga": {
                "clubs": [
                    ("Real Madrid", 400000000),
                    ("Barcelona", 300000000),
                    ("Atletico Madrid", 150000000),
                    ("Athletic Bilbao", 100000000)
                ],
                "players": [
                    ("Vinicius Jr", 180000000, "FWD", 24, "Real Madrid"),
                    ("Pedri", 100000000, "MID", 22, "Barcelona"),
                    ("Antoine Griezmann", 60000000, "FWD", 33, "Atletico Madrid"),
                    ("Nico Williams", 80000000, "FWD", 22, "Athletic Bilbao")
                ]
            },
            "serie_a": {
                "clubs": [
                    ("Inter Milan", 200000000),
                    ("AC Milan", 180000000),
                    ("Juventus", 220000000),
                    ("Roma", 120000000)
                ],
                "players": [
                    ("Lautaro Martinez", 110000000, "FWD", 27, "Inter Milan"),
                    ("Rafael Leao", 90000000, "FWD", 25, "AC Milan"),
                    ("Dusan Vlahovic", 80000000, "FWD", 24, "Juventus"),
                    ("Paulo Dybala", 50000000, "MID", 31, "Roma")
                ]
            }
        }
        
        if theme not in themes:
            await interaction.response.send_message("❌ Invalid theme! Choose: premier_league, la_liga, serie_a", ephemeral=True)
            return
        
        theme_data = themes[theme]
        clubs_added = 0
        players_added = 0
        
        # Add clubs
        for club_name, budget in theme_data["clubs"]:
            club_id = f"{interaction.guild.id}_{club_name.lower().replace(' ', '_')}"
            if not self.db.get_club(club_id):
                if self.db.add_club(club_id, club_name, budget):
                    clubs_added += 1
        
        # Add players
        for player_name, value, position, age, club_name in theme_data["players"]:
            player_id = f"{interaction.guild.id}_{player_name.lower().replace(' ', '_')}"
            club_id = f"{interaction.guild.id}_{club_name.lower().replace(' ', '_')}"
            
            if not self.db.get_player(player_id) and self.db.get_club(club_id):
                if self.db.add_player(player_id, player_name, value, club_id, position, age):
                    players_added += 1
        
        embed = discord.Embed(
            title="⚡ Quick Setup Complete",
            color=discord.Color.green(),
            description=f"Set up {theme.replace('_', ' ').title()} theme!"
        )
        
        embed.add_field(name="🏟️ Clubs Added", value=str(clubs_added), inline=True)
        embed.add_field(name="👥 Players Added", value=str(players_added), inline=True)
        embed.add_field(name="🎯 Theme", value=theme.replace('_', ' ').title(), inline=True)
        
        embed.set_footer(text="Use /list_clubs and /list_players to see the setup!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="custom_embed", description="Create a custom embed with image and advanced options")
    @app_commands.describe(
        title="Embed title",
        description="Embed description",
        color="Embed color (hex code like #FF0000 or color name)",
        image="Upload image from album",
        thumbnail="Upload thumbnail image from album",
        footer="Footer text",
        author_name="Author name",
        author_icon="Upload author icon from album"
    )
    async def custom_embed(self, interaction: discord.Interaction, title: str = None, description: str = None, 
                          color: str = None, image: discord.Attachment = None, thumbnail: discord.Attachment = None, 
                          footer: str = None, author_name: str = None, author_icon: discord.Attachment = None):
        """Create custom embed with images"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Default values if none provided
        if not title and not description and not image:
            await interaction.response.send_message("❌ Please provide at least a title, description, or image!", ephemeral=True)
            return
        
        # Parse color
        embed_color = discord.Color.blue()  # Default color
        if color:
            try:
                if color.startswith('#'):
                    embed_color = discord.Color(int(color[1:], 16))
                else:
                    # Try common color names
                    color_map = {
                        'red': discord.Color.red(),
                        'blue': discord.Color.blue(),
                        'green': discord.Color.green(),
                        'yellow': discord.Color.yellow(),
                        'orange': discord.Color.orange(),
                        'purple': discord.Color.purple(),
                        'gold': discord.Color.gold(),
                        'pink': discord.Color.magenta(),
                        'black': discord.Color(0x000000),
                        'white': discord.Color(0xFFFFFF)
                    }
                    embed_color = color_map.get(color.lower(), discord.Color.blue())
            except:
                embed_color = discord.Color.blue()
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=embed_color
        )
        
        # Add author if provided
        if author_name:
            embed.set_author(name=author_name, icon_url=author_icon.url if author_icon else None)
        
        # Add main image if provided
        if image:
            embed.set_image(url=image.url)
        
        # Add thumbnail if provided
        if thumbnail:
            embed.set_thumbnail(url=thumbnail.url)
        
        # Add footer if provided
        if footer:
            embed.set_footer(text=footer)
        
        # Add timestamp
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="club_showcase", description="Create a beautiful club showcase with image")
    @app_commands.describe(
        club="Club name",
        image="Upload club image/logo from album",
        background_color="Background color (hex or name)"
    )
    async def club_showcase(self, interaction: discord.Interaction, club: str, image: discord.Attachment = None, background_color: str = "blue"):
        """Create club showcase embed"""
        club_id = f"{interaction.guild.id}_{club.lower().replace(' ', '_')}"
        club_data = self.db.get_club(club_id)
        
        if not club_data:
            await interaction.response.send_message(f"❌ Club '{club}' not found!", ephemeral=True)
            return
        
        players = self.db.get_players()
        club_players = [players[pid] for pid in club_data.get('players', []) if pid in players]
        
        # Parse color
        embed_color = discord.Color.blue()
        try:
            if background_color.startswith('#'):
                embed_color = discord.Color(int(background_color[1:], 16))
            else:
                color_map = {
                    'red': discord.Color.red(), 'blue': discord.Color.blue(), 'green': discord.Color.green(),
                    'yellow': discord.Color.yellow(), 'orange': discord.Color.orange(), 'purple': discord.Color.purple(),
                    'gold': discord.Color.gold(), 'pink': discord.Color.magenta()
                }
                embed_color = color_map.get(background_color.lower(), discord.Color.blue())
        except:
            embed_color = discord.Color.blue()
        
        # Calculate stats
        total_value = sum(p['value'] for p in club_players)
        avg_value = total_value / len(club_players) if club_players else 0
        most_valuable = max(club_players, key=lambda x: x['value']) if club_players else None
        
        # Position counts
        positions = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}
        ages = []
        
        for player in club_players:
            pos = player.get('position', '')
            if pos in positions:
                positions[pos] += 1
            if player.get('age', 0) > 0:
                ages.append(player['age'])
        
        embed = discord.Embed(
            title=f"🏟️ {club_data['name']} - Club Showcase",
            description="*Elite Football Club Profile*",
            color=embed_color
        )
        
        # Add main image
        if image:
            embed.set_image(url=image.url)
        
        # Club stats
        embed.add_field(
            name="💰 Financial Status",
            value=f"💎 **Squad Value:** €{total_value:,.0f}\n💵 **Available Budget:** €{club_data['budget']:,.0f}\n📊 **Total Worth:** €{(total_value + club_data['budget']):,.0f}",
            inline=True
        )
        
        embed.add_field(
            name="👥 Squad Overview",
            value=f"🔢 **Total Players:** {len(club_players)}\n💎 **Average Value:** €{avg_value:,.0f}\n⭐ **Star Player:** {most_valuable['name'] if most_valuable else 'None'}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Squad Formation",
            value=f"🥅 **GK:** {positions['GK']}\n🛡️ **DEF:** {positions['DEF']}\n⚽ **MID:** {positions['MID']}\n🎯 **FWD:** {positions['FWD']}",
            inline=True
        )
        
        if ages:
            avg_age = sum(ages) / len(ages)
            embed.add_field(
                name="🎂 Age Statistics",
                value=f"📊 **Average Age:** {avg_age:.1f} years\n📈 **Age Range:** {min(ages)}-{max(ages)} years",
                inline=True
            )
        
        # Add top 3 players
        if club_players:
            top_players = sorted(club_players, key=lambda x: x['value'], reverse=True)[:3]
            top_players_text = ""
            medals = ["🥇", "🥈", "🥉"]
            
            for i, player in enumerate(top_players):
                age_text = f" ({player['age']}yo)" if player.get('age', 0) > 0 else ""
                pos_text = f" [{player.get('position', 'N/A')}]" if player.get('position') else ""
                top_players_text += f"{medals[i]} **{player['name']}**{age_text}{pos_text}\n💰 €{player['value']:,.0f}\n\n"
            
            embed.add_field(name="⭐ Top Players", value=top_players_text, inline=False)
        
        embed.set_footer(text=f"📅 Established • {interaction.guild.name} League")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="player_card", description="Create a player trading card with image")
    @app_commands.describe(
        player="Player name",
        image="Upload player image from album",
        card_style="Card style: classic, modern, or premium"
    )
    async def player_card(self, interaction: discord.Interaction, player: str, image: discord.Attachment = None, card_style: str = "modern"):
        """Create player trading card"""
        player_id = f"{interaction.guild.id}_{player.lower().replace(' ', '_')}"
        player_data = self.db.get_player(player_id)
        
        if not player_data:
            await interaction.response.send_message(f"❌ Player '{player}' not found!", ephemeral=True)
            return
        
        # Card styles
        styles = {
            "classic": {"color": discord.Color.gold(), "emoji": "⚡", "style_name": "Classic"},
            "modern": {"color": discord.Color.blue(), "emoji": "🔥", "style_name": "Modern"},
            "premium": {"color": discord.Color.purple(), "emoji": "💎", "style_name": "Premium"}
        }
        
        style = styles.get(card_style.lower(), styles["modern"])
        
        # Get club info
        club_name = "Free Agent"
        if player_data.get('club_id'):
            club = self.db.get_club(player_data['club_id'])
            if club:
                club_name = club['name']
        
        # Rating based on value (simplified)
        value = player_data['value']
        if value >= 100000000:
            rating = "99"
            tier = "LEGEND"
        elif value >= 50000000:
            rating = str(90 + int((value - 50000000) / 5555555))
            tier = "ELITE"
        elif value >= 20000000:
            rating = str(80 + int((value - 20000000) / 3333333))
            tier = "GOLD"
        elif value >= 5000000:
            rating = str(70 + int((value - 5000000) / 1500000))
            tier = "SILVER"
        else:
            rating = str(60 + int(value / 83333))
            tier = "BRONZE"
        
        embed = discord.Embed(
            title=f"{style['emoji']} {player_data['name']} - {tier} CARD",
            description=f"*{style['style_name']} Trading Card*",
            color=style['color']
        )
        
        if image:
            embed.set_image(url=image.url)
        
        # Card details
        embed.add_field(
            name="📊 Player Stats",
            value=f"🎯 **Overall:** {rating}\n💎 **Value:** €{value:,.0f}\n🎂 **Age:** {player_data.get('age', 'N/A')}\n🎭 **Position:** {player_data.get('position', 'N/A')}",
            inline=True
        )
        
        embed.add_field(
            name="⚽ Club Info",
            value=f"🏟️ **Current Club:** {club_name}\n🎴 **Card Tier:** {tier}\n✨ **Style:** {style['style_name']}",
            inline=True
        )
        
        # Contract info if available
        if player_data.get('contract_expires'):
            try:
                expiry_date = datetime.fromisoformat(player_data['contract_expires'])
                days_left = (expiry_date - datetime.now()).days
                contract_status = "🔴 Expiring Soon" if days_left <= 30 else "🟢 Active"
                
                embed.add_field(
                    name="📄 Contract",
                    value=f"{contract_status}\n📅 **Expires:** {expiry_date.strftime('%Y-%m-%d')}\n⏰ **Days Left:** {days_left}",
                    inline=True
                )
            except:
                pass
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/53/53283.png")  # Football icon
        embed.set_footer(text=f"Card ID: {player_id.split('_')[-1]} • {interaction.guild.name}")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="league_banner", description="Create a league banner with custom styling")
    @app_commands.describe(
        title="Banner title",
        subtitle="Banner subtitle",
        image="Upload background image from album",
        banner_color="Banner color theme"
    )
    async def league_banner(self, interaction: discord.Interaction, title: str = None, subtitle: str = None, 
                           image: discord.Attachment = None, banner_color: str = "gold"):
        """Create league banner"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Get league stats
        clubs = self.db.get_clubs()
        players = self.db.get_players()
        transfers = self.db.get_transfers()
        
        guild_clubs = {k: v for k, v in clubs.items() if k.startswith(str(interaction.guild.id))}
        guild_players = {k: v for k, v in players.items() if k.startswith(str(interaction.guild.id))}
        guild_transfers = [t for t in transfers if t['player_id'].startswith(str(interaction.guild.id))]
        
        # Parse color
        color_map = {
            'gold': discord.Color.gold(),
            'red': discord.Color.red(),
            'blue': discord.Color.blue(),
            'green': discord.Color.green(),
            'purple': discord.Color.purple()
        }
        embed_color = color_map.get(banner_color.lower(), discord.Color.gold())
        
        # Calculate stats
        total_club_value = sum(c['budget'] for c in guild_clubs.values())
        total_player_value = sum(p['value'] for p in guild_players.values())
        total_league_value = total_club_value + total_player_value
        
        embed = discord.Embed(
            title=title or f"🏆 {interaction.guild.name} Football League",
            description=subtitle or "*The Ultimate Football Management Experience*",
            color=embed_color
        )
        
        if image:
            embed.set_image(url=image.url)
        
        embed.add_field(
            name="📊 League Overview",
            value=f"🏟️ **Clubs:** {len(guild_clubs)}\n👥 **Players:** {len(guild_players)}\n🔄 **Transfers:** {len(guild_transfers)}",
            inline=True
        )
        
        embed.add_field(
            name="💰 Financial Stats",
            value=f"💎 **Total Value:** €{total_league_value:,.0f}\n🏦 **Club Budgets:** €{total_club_value:,.0f}\n⚽ **Player Market:** €{total_player_value:,.0f}",
            inline=True
        )
        
        # Top club by value
        if guild_clubs:
            richest_club = max(guild_clubs.values(), key=lambda x: x['budget'])
            embed.add_field(
                name="👑 League Leaders",
                value=f"💰 **Richest Club:** {richest_club['name']}\n💎 **Budget:** €{richest_club['budget']:,.0f}",
                inline=True
            )
        
        # Most valuable player
        if guild_players:
            most_valuable = max(guild_players.values(), key=lambda x: x['value'])
            embed.add_field(
                name="⭐ Star Player",
                value=f"🌟 **{most_valuable['name']}**\n💎 **Value:** €{most_valuable['value']:,.0f}",
                inline=True
            )
        
        embed.set_footer(text="🚀 Powered by Advanced Football Management System")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reset_all", description="Reset entire system - ALL data will be deleted!")
    async def reset_all(self, interaction: discord.Interaction):
        """Reset all system data"""
        if not check_admin(interaction):
            await interaction.response.send_message("❌ Administrator permissions required!", ephemeral=True)
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ SYSTEM RESET WARNING",
            description="**This will permanently delete ALL data including:**\n\n🏟️ All Clubs\n👥 All Players\n💰 All Financial Records\n🔄 All Transfer History\n📊 All Statistics\n\n**This action CANNOT be undone!**",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="💀 Data to be deleted",
            value=f"• {len(self.db.get_clubs())} Clubs\n• {len(self.db.get_players())} Players\n• {len(self.db.get_transfers())} Transfers",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Authorization Required",
            value="Only server administrators can perform this action",
            inline=True
        )
        
        embed.set_footer(text="Type 'CONFIRM RESET' exactly to proceed or wait 30 seconds to cancel")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
        
        # Wait for confirmation
        def check(m):
            return (m.author == interaction.user and 
                   m.channel == interaction.channel and 
                   m.content == "CONFIRM RESET")
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            # Perform reset
            import os
            data_files = ['data/clubs.json', 'data/players.json', 'data/transfers.json']
            
            for file_path in data_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Reinitialize database
            self.db = self.bot.db = Database()
            
            # Create success embed
            success_embed = discord.Embed(
                title="✅ SYSTEM RESET COMPLETED",
                description="All data has been successfully deleted and the system has been reset to factory defaults.",
                color=discord.Color.green()
            )
            
            success_embed.add_field(
                name="🧹 Cleaned Data",
                value="• All clubs removed\n• All players removed\n• All transfers cleared\n• All financial records reset",
                inline=True
            )
            
            success_embed.add_field(
                name="🚀 Ready for Setup",
                value="Use `/quick_setup` to populate with sample data or start adding clubs and players manually.",
                inline=True
            )
            
            success_embed.set_footer(text=f"Reset performed by {interaction.user.display_name}")
            success_embed.timestamp = datetime.now()
            
            await msg.reply(embed=success_embed)
            
        except:
            # Timeout or invalid confirmation
            cancel_embed = discord.Embed(
                title="❌ RESET CANCELLED",
                description="System reset was cancelled. No data was modified.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=cancel_embed)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))