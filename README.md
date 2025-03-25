# 💖 Pink Discord Moderation Bot 💖

A powerful Discord bot focused on moderation and security with a delightful pink theme!

![Discord Bot](https://img.shields.io/badge/Discord%20Bot-Pink%20Moderation-ff1493)

## ✨ Features

- 🛡️ **Powerful Moderation Commands**: kick, ban, mute, warn, purge...
- 🔒 **Security Systems**: Anti-spam, raid protection, bad word filtering
- 💕 **Beautiful Pink Theme**: All embeds feature a gorgeous pink color palette
- 🔧 **Fully Configurable**: Easy to customize through the config file

## 🚀 Quick Setup

1. Clone this repository

2. Install the required packages in the requirements.txt file

3. Set up your `.env` file with your Discord bot token:
   (replace your_discord_bot_token_here with your bots token)
```
BOT_TOKEN=your_discord_bot_token_here
```

4. Run the bot:
```bash
python main.py
```

## 🔑 Getting a Discord Bot Token

1. Visit the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a New Application
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot token
5. Paste this token in your `.env` file

## 🤖 Inviting Your Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application and go to the "OAuth2" tab
3. In the "URL Generator", select the "bot" scope
4. Select the permissions your bot needs (Admin recommended for all features)
5. Copy the generated URL and open it in your browser to invite the bot

## 📜 Commands

### 🔨 Moderation Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!kick` | Kick a user from the server | `!kick @user [reason]` |
| `!ban` | Ban a user from the server | `!ban @user [reason]` |
| `!unban` | Unban a user | `!unban user_id` |
| `!mute` | Mute a user for specified time | `!mute @user [duration] [reason]` |
| `!unmute` | Unmute a user | `!unmute @user` |
| `!warn` | Warn a user | `!warn @user [reason]` |
| `!warnings` | View a user's warnings | `!warnings @user` |
| `!clearwarns` | Clear warnings for a user | `!clearwarns @user` |
| `!purge` | Delete messages | `!purge [amount]` |
| `!lockdown` | Lock a channel | `!lockdown [reason]` |
| `!unlock` | Unlock a channel | `!unlock` |

### ℹ️ Information Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!help` | Display help message | `!help [command]` |
| `!userinfo` | Show user information | `!userinfo [@user]` |
| `!serverinfo` | Show server information | `!serverinfo` |
| `!botinfo` | Show bot information | `!botinfo` |
| `!ping` | Check bot latency | `!ping` |
| `!avatar` | Show user's avatar | `!avatar [@user]` |
| `!uptime` | Show bot uptime | `!uptime` |

### ⚙️ Configuration Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!config` | View current configuration | `!config` |
| `!setprefix` | Change the command prefix | `!setprefix <new_prefix>` |
| `!setlogchannel` | Set moderation log channel | `!setlogchannel #channel` |
| `!togglefeature` | Toggle features on/off | `!togglefeature <feature>` |

## 🔧 Customization

You can easily customize the bot by editing the `config.py` file, which contains settings for:

- Command prefix
- Bot activity status
- Color themes
- Cooldowns and rate limits
- Anti-spam and automod settings
- Moderation actions and durations
- And more!

## 📋 Requirements

- Python 3.8 or higher
- discord.py 2.3.2
- Other dependencies listed in `requirements.txt`

## 🌟 Support & Contribution

Feel free to open issues or pull requests if you want to contribute to the project!

## 📝 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

---

Made with 💖 by mushy420
