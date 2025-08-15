# Overview

This is a comprehensive Discord bot for managing football clubs, built with Python and discord.py. The bot provides a complete management system for football clubs, players, transfers, and finances using slash commands. It features a modular cog-based architecture and includes a keep-alive web server for reliable hosting on platforms like Render.com.

The bot allows server administrators to create and manage football clubs, add players with market values, handle transfers between clubs with proper financial calculations, and maintain comprehensive financial records. All management operations are restricted to users with administrator permissions.

# User Preferences

Preferred communication style: Simple, everyday language.
Language: Arabic and English support
Feature requests: Added comprehensive advanced features including statistics, admin tools, player management enhancements, visual embed commands with album image upload support, complete system reset functionality, and detailed README with Render.com deployment instructions.

# System Architecture

## Bot Architecture
The application follows a modular cog-based architecture using discord.py's extension system. The main bot class (`FootballBot`) inherits from `commands.Bot` and loads separate cogs for different functionalities:

- **Club Management Cog**: Handles club creation, removal, and information display
- **Player Management Cog**: Manages player addition, removal, and statistics
- **Enhanced Player Management Cog**: Advanced features including positions, ages, contracts, and squad analysis
- **Transfer Management Cog**: Processes player transfers between clubs with financial validation
- **Financial Management Cog**: Handles budget operations and financial reporting
- **Advanced Statistics Cog**: Provides league tables, comparisons, rankings, and market analysis
- **Admin Tools Cog**: Administrative utilities including rename, backup, data management, and analytics

## Data Storage
The system uses JSON files for data persistence, avoiding the complexity of a full database setup:

- **clubs.json**: Stores club information including names, budgets, and metadata
- **players.json**: Contains player data with market values and club assignments
- **transfers.json**: Maintains transfer history and transaction records

Each JSON file includes a `last_updated` timestamp for tracking data modifications.

## Permission System
A dedicated permission utility (`utils/permissions.py`) handles authorization by checking:
- Discord administrator permissions
- Server ownership status  
- Custom admin role assignments (Admin, Administrator, Moderator, Staff)

All management commands require administrator privileges, ensuring secure operations.

## Keep-Alive System
A Flask web server runs in a separate thread to provide uptime monitoring with three endpoints:
- `/` - Status page with HTML interface
- `/health` - JSON health check for monitoring services
- `/ping` - Simple ping endpoint for uptime checks

## Command Structure
The bot uses Discord's slash command system exclusively with 59+ commands across 10 modular cogs:
- **Club Management** (4 commands): Basic club operations
- **Player Management** (6 commands): Core player operations
- **Enhanced Player Management** (6 commands): Advanced player features
- **Transfer Management** (4 commands): Transfer operations
- **Financial Management** (5 commands): Budget and financial operations
- **Advanced Statistics** (6 commands): Analytics and comparisons
- **Admin Tools** (9 commands): Administrative utilities including complete system reset
- **Extra Commands** (7 commands): Price manipulation and market simulation
- **Utility Commands** (8 commands): Data import/export, quick setup, and custom embeds
- **Visual Embeds** (6 commands): Advanced image gallery and visual design commands

## Guild-Based Data Isolation
All data is scoped to specific Discord guilds using a `guild_id` prefix system, ensuring complete data isolation between different servers using the bot.

# External Dependencies

## Core Framework
- **discord.py**: Primary Discord API wrapper for bot functionality and slash commands
- **Flask**: Lightweight web server for keep-alive functionality and status monitoring

## Python Standard Library
- **json**: Data serialization and persistence
- **logging**: Comprehensive logging system with file and console output
- **threading**: Multi-threaded execution for web server and bot operations
- **datetime**: Timestamp management for data tracking
- **os**: Environment variable handling and file system operations

## Hosting Requirements
- **Environment Variables**: Requires `DISCORD_BOT_TOKEN` for Discord API authentication
- **File System**: Needs write access to `data/` directory for JSON file storage
- **Network Access**: Requires outbound HTTPS for Discord API and inbound HTTP for keep-alive server

## Optional Integrations
The architecture supports easy extension for:
- Database backends (MySQL, PostgreSQL, SQLite)
- External APIs for player statistics or market data
- Advanced web dashboards beyond the simple status page
- Webhook integrations for transfer notifications