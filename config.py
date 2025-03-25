
# Bot Configuration

# Command prefix
PREFIX = "!"

# Bot activity status
ACTIVITY = "!help | Protecting the server"

# Color themes (in hex)
COLORS = {
    "main": 0xFF1493,  # Deep Pink
    "success": 0xFF69B4,  # Hot Pink
    "error": 0xFF0066,  # Strong Pink
    "warning": 0xFFB6C1,  # Light Pink
    "info": 0xFFC0CB,  # Pink
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cooldowns and rate limits (in seconds)
COMMAND_COOLDOWN = 3
BAN_COMMAND_COOLDOWN = 5
KICK_COMMAND_COOLDOWN = 5

# Anti-spam settings
SPAM_THRESHOLD = 5  # Number of messages
SPAM_INTERVAL = 5   # In seconds
SPAM_MUTE_DURATION = 300  # 5 minutes in seconds

# Auto-mod settings
ENABLE_ANTI_SPAM = True
ENABLE_ANTI_RAID = True
ENABLE_BAD_WORDS_FILTER = True

# Bad words list (can be extended)
BAD_WORDS = ["badword1", "badword2", "badword3"]

# Moderation settings
DEFAULT_MUTE_DURATION = 3600  # 1 hour in seconds
MAX_WARN_COUNT = 3  # Number of warnings before taking action
WARN_ACTION = "mute"  # Options: "mute", "kick", "ban"

# Raid protection
RAID_JOIN_THRESHOLD = 5  # Number of joins
RAID_JOIN_INTERVAL = 10  # In seconds
RAID_ACTION = "lockdown"  # Options: "lockdown", "verification"

# Logging channels (IDs, set to None if not used)
MOD_LOG_CHANNEL = None
JOIN_LEAVE_CHANNEL = None
