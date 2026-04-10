# PixelGuard Discord Bot

<div align="center">

![PixelGuard Logo](https://img.shields.io/badge/PixelGuard-Discord%20Bot-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Discord.py](https://img.shields.io/badge/discord.py-2.7%2B-blue?style=for-the-badge&logo=discord)

A comprehensive Discord bot with welcome features, moderation commands, honeypot spam detection, and picture functionality.

[![Stars](https://img.shields.io/github/stars/yourusername/pixelguard-bot?style=social)](https://github.com/yourusername/pixelguard-bot)
[![Forks](https://img.shields.io/github/forks/yourusername/pixelguard-bot?style=social)](https://github.com/yourusername/pixelguard-bot)
[![Issues](https://img.shields.io/github/issues/yourusername/pixelguard-bot)](https://github.com/yourusername/pixelguard-bot/issues)

</div>

## Features

### 🎉 Welcome System
- Automated welcome messages for new members
- Member information display (account age, server count)
- Customizable welcome channel

### 🛡️ Moderation Commands
- `/ban` - Ban a user from the server
- `/softban` - Ban and immediately unban (deletes 7 days of messages)
- `/kick` - Kick a user from the server
- `/mute` - Mute a user for a specified duration
- `/unmute` - Unmute a user

### 🍯 Honeypot System
- Automatic spam trap detection
- Logs users who post in restricted channels
- Automatic message deletion and user warnings

### 🚨 Anti-Spam Protection
- Automatic spam detection (5 messages in 5 seconds)
- Temporary timeouts for spammers
- Configurable thresholds

### 🖼️ Picture Commands
- `/picture` - Shows the bot's avatar
- `/picture generate` - Generates a random image with shapes

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Discord account with server admin permissions

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Enable the following bot intents:
   - Server Members Intent
   - Message Content Intent
   - Message Intent
   - Ban Members (for moderation)
   - Kick Members (for moderation)
   - Moderate Members (for timeouts)

### 4. Configure Bot Permissions
In the Discord Developer Portal, under your bot's settings:
1. Go to "OAuth2" → "URL Generator"
2. Select these scopes:
   - `bot`
   - `applications.commands`
3. Select these bot permissions:
   - Administrator (recommended) or individual permissions:
     - Send Messages
     - Embed Links
     - Attach Files
     - Read Message History
     - Kick Members
     - Ban Members
     - Moderate Members
     - Manage Channels
     - Manage Roles
     - Read Messages/View Channels

### 5. Set Up Environment Variables
1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your values:
```
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
WELCOME_CHANNEL_ID=your_welcome_channel_id_here
LOGS_CHANNEL_ID=your_logs_channel_id_here
```

#### Getting the IDs:
- **DISCORD_TOKEN**: From Discord Developer Portal → Bot → Reset Token
- **GUILD_ID**: Right-click your server icon in Discord → Copy Server ID (enable Developer Mode in Discord settings)
- **WELCOME_CHANNEL_ID**: Right-click the welcome channel → Copy Channel ID
- **LOGS_CHANNEL_ID**: Right-click the logs channel → Copy Channel ID

### 6. Server Setup
1. Create a channel named `honeypot` (this will be the spam trap)
2. Create a welcome channel and a logs channel
3. Make sure the bot has access to all channels

### 7. Run the Bot
```bash
python bot.py
```

## Configuration

You can modify the bot's behavior by editing `config.py`:

```python
# Bot settings
BOT_PREFIX = "!"
BOT_COLOR = 0x00ff00

# Moderation settings
MUTE_ROLE_NAME = "Muted"
HONEYPOT_CHANNEL_NAME = "honeypot"
SPAM_THRESHOLD = 5  # Messages in 5 seconds
SPAM_TIMEOUT = 10  # Seconds
```

## Command Usage

### Moderation Commands (Require appropriate permissions)
- `/ban @user [reason]` - Permanently ban a user
- `/softban @user [reason]` - Ban and immediately unban (clears messages)
- `/kick @user [reason]` - Kick a user from the server
- `/mute @user [duration_minutes] [reason]` - Mute a user (default 10 minutes)
- `/unmute @user [reason]` - Remove mute from a user

### Picture Commands
- `/picture` - Display the bot's avatar
- `/picture generate` - Generate a random colorful image

## Features in Detail

### Welcome System
When a new member joins:
- Sends an embedded welcome message to the welcome channel
- Displays member avatar, account creation date, and server member count
- Logs the join event to the logs channel

### Honeypot System
- Any message posted in the `honeypot` channel is immediately deleted
- The user receives a DM warning
- The event is logged to the logs channel with full details

### Spam Detection
- Tracks message frequency per user
- If a user sends 5+ messages in 5 seconds, they receive a 10-second timeout
- All spam events are logged

### Logging
All moderation actions and security events are logged to your specified logs channel with:
- User information
- Action taken
- Reason (if provided)
- Moderator who performed the action

## Troubleshooting

### Common Issues

1. **Bot doesn't respond to commands**
   - Check that the bot has the correct permissions
   - Ensure the bot is online (check console output)
   - Verify command sync completed successfully

2. **Missing permissions error**
   - Make sure the bot has Administrator role or specific required permissions
   - Check that the bot's role is above other roles in the server hierarchy

3. **Commands not showing up**
   - Commands may take a few minutes to sync
   - Try restarting the bot
   - Check that the bot has `applications.commands` scope

4. **Honeypot not working**
   - Verify the channel name matches `HONEYPOT_CHANNEL_NAME` in config
   - Ensure the bot can read and delete messages in that channel

### Getting Help
If you encounter issues:
1. Check the console output for error messages
2. Verify all environment variables are set correctly
3. Ensure the bot has proper permissions
4. Check that Discord services are operational

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### How to Contribute
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test them thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup
1. Clone your fork: `git clone https://github.com/yourusername/pixelguard-bot.git`
2. Navigate to the project: `cd pixelguard-bot`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up your `.env` file from `.env.example`
5. Make your changes and test locally

### Contribution Guidelines
- Follow the existing code style
- Add comments for complex functionality
- Test your changes thoroughly
- Update documentation if needed
- Be respectful and constructive in PR discussions

### 🐛 Bug Reports
Found a bug? Please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)

### 💡 Feature Requests
Have an idea? Open an issue with:
- Feature description
- Use case
- Implementation ideas (optional)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Pillow](https://github.com/python-pillow/Pillow) - Image generation
- The Discord community for inspiration and feedback

---

<div align="center">
Made with ❤️ by the community
</div>
