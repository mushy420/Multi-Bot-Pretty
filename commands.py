
import discord
from discord.ext import commands
import asyncio
import datetime
import logging
import config
from typing import Union, Optional

logger = logging.getLogger("bot.commands")

class Moderation(commands.Cog):
    """Moderation commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.spam_check = {}
        self.raid_check = []
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, config.KICK_COMMAND_COOLDOWN, commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="Error",
                description="You cannot kick someone with a role higher than or equal to yours.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        reason = reason or "No reason provided"
        try:
            await member.kick(reason=f"{reason} - By {ctx.author}")
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await ctx.send(embed=embed)
            
            # Log the kick
            await self.log_mod_action(ctx.guild, "Kick", member, ctx.author, reason)
            logger.info(f"{member} was kicked by {ctx.author} for: {reason}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to kick this member.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, config.BAN_COMMAND_COOLDOWN, commands.BucketType.user)
    async def ban(self, ctx, member: Union[discord.Member, discord.User], *, reason=None):
        """Ban a member from the server"""
        # Check if target is a member and has higher role
        if isinstance(member, discord.Member):
            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                embed = discord.Embed(
                    title="Error",
                    description="You cannot ban someone with a role higher than or equal to yours.",
                    color=config.COLORS["error"]
                )
                return await ctx.send(embed=embed)
        
        reason = reason or "No reason provided"
        try:
            await ctx.guild.ban(member, reason=f"{reason} - By {ctx.author}")
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention if hasattr(member, 'mention') else member.name} has been banned from the server.",
                color=config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_footer(text=f"Banned by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await ctx.send(embed=embed)
            
            # Log the ban
            await self.log_mod_action(ctx.guild, "Ban", member, ctx.author, reason)
            logger.info(f"{member} was banned by {ctx.author} for: {reason}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to ban this member.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def mute(self, ctx, member: discord.Member, duration: Optional[int] = None, *, reason=None):
        """Mute a member in the server"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="Error",
                description="You cannot mute someone with a role higher than or equal to yours.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        reason = reason or "No reason provided"
        duration = duration or config.DEFAULT_MUTE_DURATION
        
        try:
            # Use timeout feature (Discord's built-in mute)
            await member.timeout(datetime.timedelta(seconds=duration), reason=f"{reason} - By {ctx.author}")
            
            # Calculate when the mute will end
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
            
            embed = discord.Embed(
                title="Member Muted",
                description=f"{member.mention} has been muted.",
                color=config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Duration", value=f"{duration} seconds")
            embed.add_field(name="Expires", value=f"<t:{int(end_time.timestamp())}:R>")
            embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await ctx.send(embed=embed)
            
            # Log the mute
            await self.log_mod_action(ctx.guild, "Mute", member, ctx.author, reason, duration=duration)
            logger.info(f"{member} was muted by {ctx.author} for {duration} seconds. Reason: {reason}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to mute this member.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        """Unmute a member in the server"""
        reason = reason or "No reason provided"
        
        try:
            # Remove timeout
            await member.timeout(None, reason=f"Unmuted: {reason} - By {ctx.author}")
            
            embed = discord.Embed(
                title="Member Unmuted",
                description=f"{member.mention} has been unmuted.",
                color=config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await ctx.send(embed=embed)
            
            # Log the unmute
            await self.log_mod_action(ctx.guild, "Unmute", member, ctx.author, reason)
            logger.info(f"{member} was unmuted by {ctx.author}. Reason: {reason}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to unmute this member.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Warn a member in the server"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="Error",
                description="You cannot warn someone with a role higher than or equal to yours.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        reason = reason or "No reason provided"
        
        # Get the user's warning count from the bot's warning system
        # For simplicity, we'll create a basic warning system here
        if not hasattr(self.bot, 'warnings'):
            self.bot.warnings = {}
            
        if ctx.guild.id not in self.bot.warnings:
            self.bot.warnings[ctx.guild.id] = {}
            
        if member.id not in self.bot.warnings[ctx.guild.id]:
            self.bot.warnings[ctx.guild.id][member.id] = []
            
        # Add the warning
        warning_count = len(self.bot.warnings[ctx.guild.id][member.id]) + 1
        warning_data = {
            'reason': reason,
            'mod': ctx.author.id,
            'time': datetime.datetime.now().isoformat()
        }
        self.bot.warnings[ctx.guild.id][member.id].append(warning_data)
        
        embed = discord.Embed(
            title="Member Warned",
            description=f"{member.mention} has been warned.",
            color=config.COLORS["warning"]
        )
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Warning Count", value=warning_count)
        embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
        
        # Send a DM to the warned user
        try:
            user_embed = discord.Embed(
                title=f"Warning in {ctx.guild.name}",
                description=f"You have been warned.",
                color=config.COLORS["warning"]
            )
            user_embed.add_field(name="Reason", value=reason)
            user_embed.add_field(name="Warning Count", value=warning_count)
            user_embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            user_embed.timestamp = datetime.datetime.now()
            
            await member.send(embed=user_embed)
        except:
            # User has DMs disabled
            pass
        
        # Log the warning
        await self.log_mod_action(ctx.guild, "Warning", member, ctx.author, reason)
        logger.info(f"{member} was warned by {ctx.author}. Reason: {reason}")
        
        # Check if action needs to be taken based on warning count
        if warning_count >= config.MAX_WARN_COUNT:
            if config.WARN_ACTION == "mute":
                await self.mute(ctx, member, config.DEFAULT_MUTE_DURATION, reason="Maximum warning count reached")
            elif config.WARN_ACTION == "kick":
                await self.kick(ctx, member, reason="Maximum warning count reached")
            elif config.WARN_ACTION == "ban":
                await self.ban(ctx, member, reason="Maximum warning count reached")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def warnings(self, ctx, member: discord.Member):
        """View warnings for a member"""
        if not hasattr(self.bot, 'warnings'):
            self.bot.warnings = {}
            
        if ctx.guild.id not in self.bot.warnings:
            self.bot.warnings[ctx.guild.id] = {}
            
        if member.id not in self.bot.warnings[ctx.guild.id]:
            self.bot.warnings[ctx.guild.id][member.id] = []
            
        warnings = self.bot.warnings[ctx.guild.id][member.id]
        
        if not warnings:
            embed = discord.Embed(
                title=f"Warnings for {member}",
                description="This member has no warnings.",
                color=config.COLORS["info"]
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"Warnings for {member}",
            description=f"This member has {len(warnings)} warning(s).",
            color=config.COLORS["info"]
        )
        
        for i, warning in enumerate(warnings, 1):
            mod = ctx.guild.get_member(warning['mod']) or "Unknown Moderator"
            time = datetime.datetime.fromisoformat(warning['time']).strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Reason:** {warning['reason']}\n**Moderator:** {mod}\n**Time:** {time}",
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def clearwarn(self, ctx, member: discord.Member, index: int = None):
        """Clear warnings for a member (specific warning or all)"""
        if not hasattr(self.bot, 'warnings'):
            self.bot.warnings = {}
            
        if ctx.guild.id not in self.bot.warnings:
            self.bot.warnings[ctx.guild.id] = {}
            
        if member.id not in self.bot.warnings[ctx.guild.id]:
            self.bot.warnings[ctx.guild.id][member.id] = []
            
        warnings = self.bot.warnings[ctx.guild.id][member.id]
        
        if not warnings:
            embed = discord.Embed(
                title="Error",
                description="This member has no warnings to clear.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if index is None:
            # Clear all warnings
            self.bot.warnings[ctx.guild.id][member.id] = []
            embed = discord.Embed(
                title="Warnings Cleared",
                description=f"All warnings for {member.mention} have been cleared.",
                color=config.COLORS["success"]
            )
        else:
            try:
                index = int(index) - 1  # Convert to 0-based index
                if index < 0 or index >= len(warnings):
                    embed = discord.Embed(
                        title="Error",
                        description=f"Invalid warning index. Please specify a number between 1 and {len(warnings)}.",
                        color=config.COLORS["error"]
                    )
                    return await ctx.send(embed=embed)
                
                # Remove the specific warning
                removed = self.bot.warnings[ctx.guild.id][member.id].pop(index)
                embed = discord.Embed(
                    title="Warning Removed",
                    description=f"Warning {index + 1} for {member.mention} has been removed.",
                    color=config.COLORS["success"]
                )
                embed.add_field(name="Removed Warning", value=removed['reason'])
            except ValueError:
                embed = discord.Embed(
                    title="Error",
                    description="Please provide a valid warning number.",
                    color=config.COLORS["error"]
                )
                return await ctx.send(embed=embed)
        
        embed.set_footer(text=f"Cleared by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
        
        # Log the action
        action = "Clear All Warnings" if index is None else f"Clear Warning #{index + 1}"
        await self.log_mod_action(ctx.guild, action, member, ctx.author)
        logger.info(f"{action} for {member} by {ctx.author}")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def purge(self, ctx, amount: int, member: discord.Member = None):
        """Purge messages from a channel"""
        if amount <= 0 or amount > 1000:
            embed = discord.Embed(
                title="Error",
                description="Please provide a valid amount between 1 and 1000.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        def check(message):
            if member:
                return message.author == member
            return True
        
        try:
            # Delete the command message first
            await ctx.message.delete()
            
            # Then purge the specified amount of messages
            deleted = await ctx.channel.purge(limit=amount, check=check)
            
            embed = discord.Embed(
                title="Messages Purged",
                description=f"Successfully deleted {len(deleted)} messages.",
                color=config.COLORS["success"]
            )
            if member:
                embed.description += f" (from {member.mention})"
            
            message = await ctx.send(embed=embed)
            
            # Delete the confirmation message after 3 seconds
            await asyncio.sleep(3)
            await message.delete()
            
            # Log the purge
            target = member.mention if member else "everyone"
            await self.log_mod_action(ctx.guild, "Purge", target, ctx.author, f"{len(deleted)} messages")
            logger.info(f"{ctx.author} purged {len(deleted)} messages in {ctx.channel.name} from {target}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to delete messages.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to delete messages: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def lockdown(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        """Lock down a channel or the current channel"""
        channel = channel or ctx.channel
        reason = reason or "No reason provided"
        
        try:
            # Update permissions for the default role (@everyone)
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            
            embed = discord.Embed(
                title="Channel Locked",
                description=f"{channel.mention} has been locked down.",
                color=config.COLORS["warning"]
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_footer(text=f"Locked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await ctx.send(embed=embed)
            
            # Log the lockdown
            await self.log_mod_action(ctx.guild, "Lockdown", channel.name, ctx.author, reason)
            logger.info(f"{ctx.author} locked down {channel.name}. Reason: {reason}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to modify channel permissions.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def unlock(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        """Unlock a channel or the current channel"""
        channel = channel or ctx.channel
        reason = reason or "No reason provided"
        
        try:
            # Update permissions for the default role (@everyone)
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = None  # Reset to default
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            
            embed = discord.Embed(
                title="Channel Unlocked",
                description=f"{channel.mention} has been unlocked.",
                color=config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason)
            embed.set_footer(text=f"Unlocked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await ctx.send(embed=embed)
            
            # Log the unlock
            await self.log_mod_action(ctx.guild, "Unlock", channel.name, ctx.author, reason)
            logger.info(f"{ctx.author} unlocked {channel.name}. Reason: {reason}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error",
                description="I don't have permission to modify channel permissions.",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config.COLORS["error"]
            )
            await ctx.send(embed=embed)
    
    async def log_mod_action(self, guild, action, target, moderator, reason=None, duration=None):
        """Log moderation actions to the specified channel"""
        if config.MOD_LOG_CHANNEL is None:
            return
        
        log_channel = self.bot.get_channel(config.MOD_LOG_CHANNEL)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"{action} Action",
            color=config.COLORS["info"]
        )
        
        # Target can be a member, user, or channel name
        if isinstance(target, (discord.Member, discord.User)):
            embed.add_field(name="Target", value=f"{target.mention} ({target.id})")
        else:
            embed.add_field(name="Target", value=str(target))
        
        embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator.id})")
        
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
            
        if duration:
            embed.add_field(name="Duration", value=f"{duration} seconds", inline=False)
        
        embed.timestamp = datetime.datetime.now()
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass

    # Event listeners for auto-moderation
    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-moderation for messages"""
        if message.author.bot or not message.guild:
            return
        
        # Skip messages from moderators/admins
        if message.author.guild_permissions.manage_messages:
            return
        
        # Anti-spam check
        if config.ENABLE_ANTI_SPAM:
            await self.check_spam(message)
        
        # Bad words filter
        if config.ENABLE_BAD_WORDS_FILTER:
            await self.check_bad_words(message)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Raid protection for member joins"""
        if config.ENABLE_ANTI_RAID:
            await self.check_raid(member)
    
    async def check_spam(self, message):
        """Check if a message is part of spam"""
        author_id = message.author.id
        channel_id = message.channel.id
        current_time = datetime.datetime.now().timestamp()
        
        # Create a key for this author in this channel
        key = f"{author_id}-{channel_id}"
        
        if key not in self.spam_check:
            self.spam_check[key] = []
        
        # Add the current message timestamp
        self.spam_check[key].append(current_time)
        
        # Clear old messages (older than the spam interval)
        self.spam_check[key] = [t for t in self.spam_check[key] if current_time - t <= config.SPAM_INTERVAL]
        
        # Check if the user has exceeded the spam threshold
        if len(self.spam_check[key]) >= config.SPAM_THRESHOLD:
            # Reset the spam counter for this user
            self.spam_check[key] = []
            
            # Mute the user
            try:
                await message.author.timeout(
                    datetime.timedelta(seconds=config.SPAM_MUTE_DURATION),
                    reason="Auto-mute for spamming"
                )
                
                # Inform the channel
                embed = discord.Embed(
                    title="Anti-Spam",
                    description=f"{message.author.mention} has been muted for spamming.",
                    color=config.COLORS["warning"]
                )
                embed.add_field(
                    name="Duration", 
                    value=f"{config.SPAM_MUTE_DURATION} seconds"
                )
                embed.timestamp = datetime.datetime.now()
                
                await message.channel.send(embed=embed)
                
                # Log the action
                await self.log_mod_action(
                    message.guild, 
                    "Auto-Mute (Spam)", 
                    message.author, 
                    self.bot.user, 
                    "Sending messages too quickly",
                    config.SPAM_MUTE_DURATION
                )
                logger.warning(f"Auto-muted {message.author} for spamming in {message.channel.name}")
                
            except:
                pass
    
    async def check_bad_words(self, message):
        """Check if a message contains bad words"""
        content = message.content.lower()
        
        for word in config.BAD_WORDS:
            if word.lower() in content:
                try:
                    # Delete the message
                    await message.delete()
                    
                    # Warn the user
                    embed = discord.Embed(
                        title="Message Deleted",
                        description="Your message was deleted for containing prohibited words.",
                        color=config.COLORS["warning"]
                    )
                    
                    await message.author.send(embed=embed)
                    
                    # Log the action
                    await self.log_mod_action(
                        message.guild,
                        "Auto-Delete (Bad Word)",
                        message.author,
                        self.bot.user,
                        f"Message contained prohibited word: {word}"
                    )
                    logger.warning(f"Deleted message from {message.author} for containing bad word: {word}")
                    
                    return  # Stop checking other words
                except:
                    pass
    
    async def check_raid(self, member):
        """Check if a new join is part of a raid"""
        current_time = datetime.datetime.now().timestamp()
        
        # Add the current join timestamp
        self.raid_check.append(current_time)
        
        # Clear old joins (older than the raid interval)
        self.raid_check = [t for t in self.raid_check if current_time - t <= config.RAID_JOIN_INTERVAL]
        
        # Check if the joins have exceeded the raid threshold
        if len(self.raid_check) >= config.RAID_JOIN_THRESHOLD:
            # Reset the raid counter
            self.raid_check = []
            
            if config.RAID_ACTION == "lockdown":
                # Lockdown all text channels
                for channel in member.guild.text_channels:
                    try:
                        overwrite = channel.overwrites_for(member.guild.default_role)
                        overwrite.send_messages = False
                        await channel.set_permissions(member.guild.default_role, overwrite=overwrite)
                    except:
                        pass
                
                # Find a channel to send the alert
                alert_channel = None
                for channel in member.guild.text_channels:
                    if channel.permissions_for(member.guild.me).send_messages:
                        alert_channel = channel
                        break
                
                if alert_channel:
                    embed = discord.Embed(
                        title="Raid Protection Activated",
                        description="A raid has been detected. All channels have been locked down.",
                        color=config.COLORS["error"]
                    )
                    embed.add_field(
                        name="Action Required",
                        value="Server administrators need to run the `!unlock` command when it's safe."
                    )
                    embed.timestamp = datetime.datetime.now()
                    
                    await alert_channel.send("@here", embed=embed)
                
                # Log the action
                await self.log_mod_action(
                    member.guild,
                    "Auto-Lockdown (Raid)",
                    "All Channels",
                    self.bot.user,
                    f"Raid detected - {config.RAID_JOIN_THRESHOLD} joins in {config.RAID_JOIN_INTERVAL} seconds"
                )
                logger.warning(f"Raid protection activated in {member.guild.name} - server locked down")


class Information(commands.Cog):
    """Information commands for server and user details"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show information about a user"""
        member = member or ctx.author
        
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        
        embed = discord.Embed(
            title=f"User Information: {member}",
            color=config.COLORS["info"]
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Nickname", value=member.nick or "None")
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>")
        embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>")
        
        if roles:
            embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles), inline=False)
        else:
            embed.add_field(name=f"Roles [0]", value="None", inline=False)
        
        embed.add_field(name="Boosting Since", value=f"<t:{int(member.premium_since.timestamp())}:R>" if member.premium_since else "Not boosting")
        
        # Get permission information
        key_permissions = []
        if member.guild_permissions.administrator:
            key_permissions.append("Administrator")
        if member.guild_permissions.ban_members:
            key_permissions.append("Ban Members")
        if member.guild_permissions.kick_members:
            key_permissions.append("Kick Members")
        if member.guild_permissions.manage_channels:
            key_permissions.append("Manage Channels")
        if member.guild_permissions.manage_guild:
            key_permissions.append("Manage Server")
        if member.guild_permissions.manage_messages:
            key_permissions.append("Manage Messages")
        if member.guild_permissions.manage_roles:
            key_permissions.append("Manage Roles")
        
        if key_permissions:
            embed.add_field(name="Key Permissions", value=", ".join(key_permissions), inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def serverinfo(self, ctx):
        """Show information about the server"""
        guild = ctx.guild
        
        # Get member status counts
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status == discord.Status.online])
        idle_members = len([m for m in guild.members if m.status == discord.Status.idle])
        dnd_members = len([m for m in guild.members if m.status == discord.Status.dnd])
        offline_members = len([m for m in guild.members if m.status == discord.Status.offline])
        
        # Get channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Get role count (excluding @everyone)
        roles = len(guild.roles) - 1
        
        embed = discord.Embed(
            title=f"{guild.name} Server Information",
            description=guild.description or "No description",
            color=config.COLORS["info"]
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Owner", value=guild.owner.mention)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>")
        embed.add_field(name="Server ID", value=guild.id)
        
        embed.add_field(name="Members", value=f"**Total:** {total_members}\n**Online:** {online_members}\n**Idle:** {idle_members}\n**DND:** {dnd_members}\n**Offline:** {offline_members}")
        embed.add_field(name="Channels", value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}")
        embed.add_field(name="Other", value=f"**Roles:** {roles}\n**Boost Level:** {guild.premium_tier}\n**Boosts:** {guild.premium_subscription_count}")
        
        # Server features
        if guild.features:
            features = ", ".join(f.replace("_", " ").title() for f in guild.features)
            embed.add_field(name="Features", value=features, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def ping(self, ctx):
        """Check the bot's latency"""
        start_time = datetime.datetime.now()
        message = await ctx.send("Pinging...")
        end_time = datetime.datetime.now()
        
        latency = (end_time - start_time).total_seconds() * 1000
        api_latency = self.bot.latency * 1000
        
        embed = discord.Embed(
            title="Pong!",
            color=config.COLORS["main"]
        )
        
        embed.add_field(name="Message Latency", value=f"{latency:.2f}ms")
        embed.add_field(name="API Latency", value=f"{api_latency:.2f}ms")
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await message.edit(content=None, embed=embed)
    
    @commands.command()
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def avatar(self, ctx, member: discord.Member = None):
        """Show a user's avatar"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"{member}'s Avatar",
            color=config.COLORS["main"]
        )
        
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def botinfo(self, ctx):
        """Show information about the bot"""
        embed = discord.Embed(
            title=f"{self.bot.user.name} Information",
            description="A moderation and security bot with a pink aesthetic!",
            color=config.COLORS["main"]
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Calculate uptime
        current_time = datetime.datetime.now()
        uptime = current_time - self.bot.start_time
        
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed.add_field(name="Uptime", value=uptime_str)
        embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.2f}ms")
        embed.add_field(name="Prefix", value=f"`{config.PREFIX}`")
        
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)))
        embed.add_field(name="Users", value=str(len(set(self.bot.get_all_members()))))
        embed.add_field(name="Commands", value=str(len(self.bot.commands)))
        
        embed.add_field(name="Library", value=f"discord.py {discord.__version__}")
        embed.add_field(name="Python", value=f"{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro}")
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def help(self, ctx, command=None):
        """Show help information for commands"""
        if command is None:
            # Show main help menu
            embed = discord.Embed(
                title="Bot Help",
                description=f"Use `{config.PREFIX}help <command>` for more information on a specific command.",
                color=config.COLORS["main"]
            )
            
            # Group commands by cog
            for cog_name, cog in self.bot.cogs.items():
                # Skip if cog has no commands
                cog_commands = [cmd for cmd in cog.get_commands() if not cmd.hidden]
                if not cog_commands:
                    continue
                
                # Add field for each cog with its commands
                command_list = ", ".join(f"`{cmd.name}`" for cmd in cog_commands)
                embed.add_field(name=cog_name, value=command_list, inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
            
        else:
            # Show help for a specific command
            cmd = self.bot.get_command(command)
            if cmd is None:
                embed = discord.Embed(
                    title="Error",
                    description=f"Command `{command}` not found.",
                    color=config.COLORS["error"]
                )
                return await ctx.send(embed=embed)
            
            embed = discord.Embed(
                title=f"Help: {cmd.name}",
                description=cmd.help or "No description available.",
                color=config.COLORS["main"]
            )
            
            # Command usage
            usage = f"{config.PREFIX}{cmd.name}"
            if cmd.signature:
                usage += f" {cmd.signature}"
            embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
            
            # Command aliases
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in cmd.aliases), inline=False)
            
            # Command cooldown
            if cmd._buckets._cooldown:
                embed.add_field(name="Cooldown", value=f"{cmd._buckets._cooldown.rate} use(s) every {cmd._buckets._cooldown.per} seconds", inline=False)
            
            # Required permissions
            required_perms = []
            for check in cmd.checks:
                check_name = check.__qualname__
                if "has_permissions" in check_name:
                    import inspect
                    source = inspect.getsource(check)
                    import re
                    perm_match = re.search(r"has_permissions\((.*?)\)", source)
                    if perm_match:
                        perms = perm_match.group(1).replace("=True", "").split(",")
                        required_perms.extend(p.strip() for p in perms)
            
            if required_perms:
                embed.add_field(name="Required Permissions", value=", ".join(f"`{perm}`" for perm in required_perms), inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)


class Config(commands.Cog):
    """Configuration commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def prefix(self, ctx, new_prefix=None):
        """View or change the bot's prefix"""
        if new_prefix is None:
            embed = discord.Embed(
                title="Current Prefix",
                description=f"The current prefix is `{config.PREFIX}`",
                color=config.COLORS["info"]
            )
            return await ctx.send(embed=embed)
        
        if len(new_prefix) > 5:
            embed = discord.Embed(
                title="Error",
                description="Prefix cannot be longer than 5 characters.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        # In a real bot, we would modify the prefix in a database
        # For this example, we'll just update the in-memory config
        config.PREFIX = new_prefix
        
        embed = discord.Embed(
            title="Prefix Changed",
            description=f"The prefix has been changed to `{new_prefix}`",
            color=config.COLORS["success"]
        )
        embed.set_footer(text=f"Changed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def setlogchannel(self, ctx, channel: discord.TextChannel):
        """Set the moderation log channel"""
        # In a real bot, we would update this in a database
        # For this example, we'll just update the in-memory config
        config.MOD_LOG_CHANNEL = channel.id
        
        embed = discord.Embed(
            title="Log Channel Set",
            description=f"Moderation logs will now be sent to {channel.mention}",
            color=config.COLORS["success"]
        )
        embed.set_footer(text=f"Set by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def toggleantispam(self, ctx):
        """Toggle the anti-spam feature"""
        # In a real bot, we would update this in a database
        # For this example, we'll just update the in-memory config
        config.ENABLE_ANTI_SPAM = not config.ENABLE_ANTI_SPAM
        
        status = "enabled" if config.ENABLE_ANTI_SPAM else "disabled"
        
        embed = discord.Embed(
            title="Anti-Spam Toggled",
            description=f"Anti-spam has been {status}.",
            color=config.COLORS["success"]
        )
        embed.set_footer(text=f"Toggled by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, config.COMMAND_COOLDOWN, commands.BucketType.user)
    async def toggleraid(self, ctx):
        """Toggle the anti-raid feature"""
        # In a real bot, we would update this in a database
        # For this example, we'll just update the in-memory config
        config.ENABLE_ANTI_RAID = not config.ENABLE_ANTI_RAID
        
        status = "enabled" if config.ENABLE_ANTI_RAID else "disabled"
        
        embed = discord.Embed(
            title="Anti-Raid Toggled",
            description=f"Anti-raid has been {status}.",
            color=config.COLORS["success"]
        )
        embed.set_footer(text=f"Toggled by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)


# Error handling
class ErrorHandler(commands.Cog):
    """Handle errors and exceptions"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle errors from commands"""
        if hasattr(ctx.command, 'on_error'):
            return  # Command has its own error handler
        
        # Get the original error
        error = getattr(error, 'original', error)
        
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(
                title="Error",
                description="This command is currently disabled.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                title="Error",
                description="This command cannot be used in private messages.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error",
                description=f"Missing required argument: `{error.param.name}`",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Error",
                description="Invalid argument provided. Please check your input.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.BadUnionArgument):
            embed = discord.Embed(
                title="Error",
                description=f"Invalid argument provided for `{error.param.name}`.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.MissingPermissions):
            perms = [perm.replace('_', ' ').title() for perm in error.missing_permissions]
            embed = discord.Embed(
                title="Error",
                description=f"You're missing the following permissions: {', '.join(perms)}",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.BotMissingPermissions):
            perms = [perm.replace('_', ' ').title() for perm in error.missing_permissions]
            embed = discord.Embed(
                title="Error",
                description=f"I'm missing the following permissions: {', '.join(perms)}",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="Error",
                description="This command can only be used by the bot owner.",
                color=config.COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Cooldown",
                description=f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
                color=config.COLORS["warning"]
            )
            return await ctx.send(embed=embed)
        
        # Log the error
        logger.error(f"Unhandled command error: {error}", exc_info=error)
        
        # Send generic error message
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again later.",
            color=config.COLORS["error"]
        )
        
        if ctx.author.guild_permissions.administrator:
            # Add more details for admins
            embed.add_field(name="Error Details", value=str(error), inline=False)
        
        await ctx.send(embed=embed)
      
