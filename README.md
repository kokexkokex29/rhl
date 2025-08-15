# Football Club Management Discord Bot

A comprehensive Discord bot for managing football clubs, players, transfers, and finances. Built with Python and discord.py, featuring over 30 slash commands, advanced statistics, and keep-alive functionality.

## ✨ Features

### 🏟️ Club Management
- Add, remove, and rename football clubs
- Set and manage club budgets (in Euros)
- View detailed club information and squad composition
- Compare clubs head-to-head
- Generate financial reports and league tables

### 👥 Player Management
- Add players with market values, positions, and ages
- Set player positions (GK, DEF, MID, FWD)
- Manage player contracts with expiry dates
- Update player values and personal information
- Advanced player search and filtering

### 🔄 Transfer System
- Transfer players between clubs with financial validation
- Release players to free agency
- Track comprehensive transfer history
- Market activity analysis and statistics
- Profit/loss calculations for transfers

### 💰 Financial Management
- Complete budget management system
- Financial reports and club rankings
- Transfer spending analysis
- Club valuation (budget + squad value)
- Revenue and expense tracking

### 📊 Advanced Statistics
- League tables by total club value
- Top players rankings by position
- Transfer activity rankings
- Squad composition analysis
- Contract expiry monitoring
- Market value trends

### 🛠️ Admin Tools
- Rename clubs and players
- Data backup and restore functionality
- Clear all data with confirmation
- Average value calculations
- Squad needs analysis
- Most transferred players tracking

### 🛡️ Security & Permissions
- All management commands restricted to administrators
- Role-based permission system
- Secure data validation and storage
- Guild-specific data isolation

### 🌐 Keep-Alive System
- Built-in Flask web server for 24/7 uptime
- Status monitoring dashboard
- Health check endpoints
- Perfect for cloud hosting platforms

## 📋 Complete Command List (58+ Commands)

### Club Management (4 commands)
- `/add_club <name> [budget]` - Add a new club
- `/remove_club <name>` - Remove a club
- `/list_clubs` - Display all clubs
- `/club_info <name>` - Show club details

### Player Management (6 commands)
- `/add_player <name> <value> [club] [position] [age]` - Add a new player
- `/remove_player <name>` - Remove a player
- `/update_player_value <name> <value>` - Update player value
- `/list_players` - Show all players
- `/player_info <name>` - Player details
- `/free_agents` - List unattached players

### Enhanced Player Management (6 commands)
- `/set_player_position <player> <position>` - Set player position
- `/set_player_age <player> <age>` - Set player age
- `/set_contract_expiry <player> [years]` - Set contract length
- `/players_by_position [position]` - Filter by position
- `/expiring_contracts [months]` - Show expiring contracts
- `/club_squad_analysis <club>` - Analyze squad composition

### Transfer Management (4 commands)
- `/transfer_player <player> <to_club> <amount>` - Transfer player
- `/release_player <player>` - Release to free agency
- `/transfer_history [player] [club]` - View transfer history
- `/market_activity` - Market statistics

### Financial Management (5 commands)
- `/set_budget <club> <budget>` - Set club budget
- `/add_budget <club> <amount>` - Add money to budget
- `/deduct_budget <club> <amount>` - Remove money from budget
- `/financial_report` - League financial overview
- `/club_finances <club>` - Club financial details

### Advanced Statistics (6 commands)
- `/top_players_league [limit]` - Top players by value
- `/richest_poorest_clubs` - Financial extremes
- `/transfer_activity_ranking` - Most active clubs
- `/league_table` - Rankings by total value
- `/compare_clubs <club1> <club2>` - Direct comparison
- `/most_transferred_players [limit]` - Transfer frequency

### Admin Tools (9 commands)
- `/rename_club <old_name> <new_name>` - Rename club
- `/rename_player <old_name> <new_name>` - Rename player
- `/backup_data` - Create data backup
- `/clear_all_data <confirm>` - Clear all data (dangerous!)
- `/average_values` - Average player values per club
- `/clubs_needing_players [threshold]` - Clubs with few players
- `/best_transfers` - Most profitable transfers
- `/contract_renewals` - Players needing contract renewal
- `/league_statistics` - Comprehensive league stats

### Extra Commands (7 commands)
- `/bulk_price_update <percentage> [club] [position]` - Update multiple player values
- `/budget_multiplier <multiplier>` - Multiply all club budgets
- `/random_player_value <min> <max> [club]` - Randomize player values
- `/salary_cap <cap> [action]` - Implement salary cap system
- `/market_crash [min_decrease] [max_decrease]` - Simulate market crash
- `/market_boom [min_increase] [max_increase]` - Simulate market boom
- `/inflation_adjustment <rate>` - Apply inflation to all values

### Utility Commands (8 commands)
- `/duplicate_player <original> <new_name> [club]` - Duplicate existing player
- `/player_age_groups` - Show age distribution analysis
- `/import_players_csv <data>` - Import players from CSV format
- `/export_data` - Export all data to file
- `/quick_setup [theme]` - Quick setup with sample data
- `/custom_embed [title] [description] [color] [image_url]` - Create custom embeds with images
- `/club_showcase <club> [image_url] [background_color]` - Beautiful club showcase
- `/player_card <player> [image_url] [card_style]` - Create player trading cards
- `/league_banner [title] [subtitle] [image_url] [banner_color]` - Create league banners

### Visual Embeds (6 commands)
- `/gallery_embed <title> <image1_url> [description] [more_images...]` - Multi-image galleries
- `/announcement_embed <type> <title> <message> [image_url]` - Official announcements
- `/match_result <home_team> <away_team> <home_score> <away_score> [images...]` - Match results
- `/stats_infographic <stat_type> [subject] [background_image]` - Statistics graphics
- `/transfer_card <player> <from_club> <to_club> <fee> [images...]` - Transfer announcements

## 🚀 Quick Setup Guide

### Prerequisites
- Discord Application with Bot Token
- Administrator permissions in your Discord server
- Python 3.8+ (for local development)

### Get Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it "Football Club Bot"
3. Go to "Bot" section → Click "Add Bot"
4. Under "Token" → Click "Copy"
5. Enable "Privileged Gateway Intents" if needed
6. Go to "OAuth2" → "URL Generator"
7. Select "bot" and "applications.commands" scopes
8. Select "Administrator" permission
9. Copy the generated URL and invite bot to your server

## 🌐 Hosting on Render.com

### Step 1: Prepare Your Repository
1. Fork this repository or upload your code to GitHub
2. Ensure all files are in the root directory

### Step 2: Create Render Service
1. Go to [Render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

```yaml
Name: football-club-bot
Region: Choose your preferred region
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
Build Command: pip install discord.py flask
Start Command: python main.py
```

### Step 3: Environment Variables
In Render Dashboard, go to Environment tab and add:
```
DISCORD_BOT_TOKEN = your_bot_token_here
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your bot will be live 24/7!

### Render.com Advantages
- ✅ Free tier available (750 hours/month)
- ✅ Automatic HTTPS and SSL
- ✅ Easy GitHub integration
- ✅ Environment variable management
- ✅ Auto-scaling and health checks
- ✅ Built-in monitoring and logs

## 🔧 Local Development

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd football-club-bot

# Install dependencies
pip install discord.py flask

# Set environment variable
export DISCORD_BOT_TOKEN="your_token_here"
# Or create .env file with:
# DISCORD_BOT_TOKEN=your_token_here

# Run the bot
python main.py
```

### Development Features
- Hot reload for code changes
- Comprehensive logging system
- JSON-based data storage
- Modular cog architecture
- Easy command testing

## 📁 Project Structure
```
football-club-bot/
├── main.py                 # Entry point
├── bot.py                  # Main bot class
├── web_server.py          # Keep-alive server
├── cogs/                  # Command modules
│   ├── club_management.py
│   ├── player_management.py
│   ├── enhanced_player_management.py
│   ├── transfer_management.py
│   ├── financial_management.py
│   ├── advanced_stats.py
│   └── admin_tools.py
├── utils/                 # Utilities
│   ├── database.py        # JSON database handler
│   └── permissions.py     # Permission system
├── data/                  # Data storage
│   ├── clubs.json
│   ├── players.json
│   └── transfers.json
├── templates/             # Web templates
│   └── status.html
└── README.md
```

## 🎮 Usage Examples

### Basic Setup
1. Invite bot to your Discord server
2. Use `/add_club Real Madrid 100000000` to create a club
3. Use `/add_player "Vinicius Jr" 80000000 "Real Madrid" FWD 24` to add a player
4. Use `/transfer_player "Vinicius Jr" Barcelona 120000000` for transfers

### Advanced Features
- Monitor contracts: `/expiring_contracts 3`
- Analyze squads: `/club_squad_analysis "Real Madrid"`
- Compare clubs: `/compare_clubs "Real Madrid" Barcelona`
- View statistics: `/league_table`

## 🛠️ Dependencies
- **discord.py** (2.5.2+) - Discord API wrapper
- **flask** (3.1.1+) - Web server for keep-alive
- **aiohttp** - Async HTTP client
- **python-dotenv** - Environment variable management

## 🤝 Support & Issues
- Create GitHub issues for bugs or feature requests
- All commands are restricted to server administrators
- Data is automatically isolated per Discord server
- Built-in backup system protects your data

## 📄 License
This project is open source and available under the MIT License.

---

**Ready to manage your football empire? Deploy now and start building your ultimate football management system!** ⚽
