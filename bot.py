import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import io
from PIL import Image, ImageDraw, ImageFont
import os
from config import Config

class ModerationBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.bans = True
        intents.moderation = True
        
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.spam_tracker = defaultdict(lambda: deque())
        self.honeypot_messages = {}
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        
        # Create mute role if it doesn't exist
        await self.setup_mute_role()
        
    async def setup_mute_role(self):
        guild = self.get_guild(Config.GUILD_ID)
        if not guild:
            return
            
        mute_role = discord.utils.get(guild.roles, name=Config.MUTE_ROLE_NAME)
        if not mute_role:
            try:
                mute_role = await guild.create_role(
                    name=Config.MUTE_ROLE_NAME,
                    reason="Creating mute role for moderation"
                )
                
                # Set permissions for all channels
                for channel in guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False)
                    
                print(f"Created mute role: {Config.MUTE_ROLE_NAME}")
            except discord.Forbidden:
                print("Don't have permission to create mute role")
    
    async def on_member_join(self, member):
        # Welcome message
        welcome_channel = self.get_channel(Config.WELCOME_CHANNEL_ID)
        if welcome_channel:
            embed = discord.Embed(
                title="Welcome to the Server!",
                description=f"Welcome {member.mention} to {member.guild.name}! 🎉",
                color=Config.BOT_COLOR
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="Member Count", value=member.guild.member_count, inline=True)
            embed.set_footer(text="Please read the rules and enjoy your stay!")
            
            await welcome_channel.send(embed=embed)
        
        # Log to logs channel
        logs_channel = self.get_channel(Config.LOGS_CHANNEL_ID)
        if logs_channel:
            embed = discord.Embed(
                title="Member Joined",
                description=f"{member.mention} has joined the server",
                color=discord.Color.green()
            )
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(name="Account Age", value=f"{(datetime.now() - member.created_at).days} days", inline=True)
            await logs_channel.send(embed=embed)
    
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Honeypot detection
        if message.channel.name == Config.HONEYPOT_CHANNEL_NAME:
            await self.handle_honeypot(message)
            return
        
        # Spam detection
        await self.check_spam(message)
        
        await self.process_commands(message)
    
    async def handle_honeypot(self, message):
        """Handle messages in honeypot channel"""
        logs_channel = self.get_channel(Config.LOGS_CHANNEL_ID)
        
        # Log the honeypot message
        if logs_channel:
            embed = discord.Embed(
                title="🍯 Honeypot Triggered",
                description=f"{message.author.mention} posted in honeypot channel",
                color=discord.Color.red()
            )
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Message", value=message.content[:500], inline=False)
            embed.add_field(name="User ID", value=message.author.id, inline=True)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            
            await logs_channel.send(embed=embed)
        
        # Delete the message
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Warn the user
        try:
            await message.author.send(
                "⚠️ You posted in a restricted channel. This is a warning. "
                "Repeated violations may result in moderation action."
            )
        except discord.Forbidden:
            pass
    
    async def check_spam(self, message):
        """Check for spam messages"""
        user_id = message.author.id
        current_time = time.time()
        
        # Add current message to tracker
        self.spam_tracker[user_id].append(current_time)
        
        # Remove old messages (older than 5 seconds)
        while (self.spam_tracker[user_id] and 
               current_time - self.spam_tracker[user_id][0] > 5):
            self.spam_tracker[user_id].popleft()
        
        # Check if user exceeded threshold
        if len(self.spam_tracker[user_id]) >= Config.SPAM_THRESHOLD:
            await self.handle_spam(message)
    
    async def handle_spam(self, message):
        """Handle spam detection"""
        logs_channel = self.get_channel(Config.LOGS_CHANNEL_ID)
        
        # Log spam detection
        if logs_channel:
            embed = discord.Embed(
                title="🚨 Spam Detected",
                description=f"{message.author.mention} is spamming messages",
                color=discord.Color.orange()
            )
            embed.add_field(name="User ID", value=message.author.id, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            await logs_channel.send(embed=embed)
        
        # Timeout the user for 10 seconds
        try:
            await message.author.timeout(timedelta(seconds=Config.SPAM_TIMEOUT), reason="Automatic spam detection")
        except discord.Forbidden:
            pass

# Initialize bot
bot = ModerationBot()

# Picture command group
@bot.tree.command(name="picture", description="Picture commands")
@app_commands.describe(action="Choose what to do with pictures")
async def picture(interaction: discord.Interaction, action: str = "show"):
    if action == "show":
        # Show bot's avatar
        embed = discord.Embed(
            title="Bot Picture",
            description="Here's my avatar!",
            color=Config.BOT_COLOR
        )
        embed.set_image(url=bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    elif action == "generate":
        # Generate a random picture
        await interaction.response.defer()
        
        # Create a simple generated image
        width, height = 400, 400
        img = Image.new('RGB', (width, height), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        
        # Add some random shapes
        draw = ImageDraw.Draw(img)
        for _ in range(10):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            radius = random.randint(10, 50)
            x2 = x1 + radius
            y2 = y1 + radius
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            draw.ellipse([x1, y1, x2, y2], fill=color)
        
        # Add PixelGuard themed text
        try:
            font = ImageFont.load_default()
            text = "PixelGuard"
            subtitle = "Generated Image"
            
            # Main text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height // 2) - text_height
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            # Subtitle
            bbox_sub = draw.textbbox((0, 0), subtitle, font=font)
            sub_width = bbox_sub[2] - bbox_sub[0]
            sub_height = bbox_sub[3] - bbox_sub[1]
            x_sub = (width - sub_width) // 2
            y_sub = (height // 2) + text_height
            draw.text((x_sub, y_sub), subtitle, fill=(200, 200, 200), font=font)
            
            # Add pixel-style border
            border_size = 10
            for i in range(border_size):
                draw.rectangle([i, i, width-i-1, height-i-1], outline=(255, 255, 255, 255-i*25))
        except:
            pass
        
        # Save to bytes
        with io.BytesIO() as output:
            img.save(output, format='PNG')
            output.seek(0)
            
            file = discord.File(fp=output, filename='generated.png')
            embed = discord.Embed(
                title="Generated Picture",
                description="Here's a randomly generated image!",
                color=Config.BOT_COLOR
            )
            embed.set_image(url="attachment://generated.png")
            await interaction.followup.send(file=file, embed=embed)

# Moderation commands
@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(user="The user to ban", reason="Reason for banning")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    await interaction.response.defer()
    
    try:
        await interaction.guild.ban(user, reason=reason)
        
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"{user.mention} has been banned",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Log to logs channel
        logs_channel = bot.get_channel(Config.LOGS_CHANNEL_ID)
        if logs_channel:
            await logs_channel.send(embed=embed)
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to ban this user.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@bot.tree.command(name="softban", description="Softban a user (ban and immediately unban)")
@app_commands.describe(user="The user to softban", reason="Reason for softbanning")
@app_commands.checks.has_permissions(ban_members=True)
async def softban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    await interaction.response.defer()
    
    try:
        await interaction.guild.ban(user, reason=reason, delete_message_days=7)
        await interaction.guild.unban(user)
        
        embed = discord.Embed(
            title="⚡ User Softbanned",
            description=f"{user.mention} has been softbanned",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Log to logs channel
        logs_channel = bot.get_channel(Config.LOGS_CHANNEL_ID)
        if logs_channel:
            await logs_channel.send(embed=embed)
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to softban this user.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(user="The user to kick", reason="Reason for kicking")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    await interaction.response.defer()
    
    try:
        await interaction.guild.kick(user, reason=reason)
        
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"{user.mention} has been kicked",
            color=discord.Color.yellow()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Log to logs channel
        logs_channel = bot.get_channel(Config.LOGS_CHANNEL_ID)
        if logs_channel:
            await logs_channel.send(embed=embed)
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to kick this user.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@bot.tree.command(name="mute", description="Mute a user in the server")
@app_commands.describe(user="The user to mute", duration="Duration in minutes (default: 10)", reason="Reason for muting")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.User, duration: int = 10, reason: str = "No reason provided"):
    await interaction.response.defer()
    
    try:
        # Get or create mute role
        mute_role = discord.utils.get(interaction.guild.roles, name=Config.MUTE_ROLE_NAME)
        if not mute_role:
            await interaction.followup.send("Mute role not found. Please create it manually.")
            return
        
        # Apply timeout
        await user.timeout(timedelta(minutes=duration), reason=reason)
        
        # Add mute role
        await user.add_roles(mute_role, reason=reason)
        
        embed = discord.Embed(
            title="🔇 User Muted",
            description=f"{user.mention} has been muted for {duration} minutes",
            color=discord.Color.blue()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Log to logs channel
        logs_channel = bot.get_channel(Config.LOGS_CHANNEL_ID)
        if logs_channel:
            await logs_channel.send(embed=embed)
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to mute this user.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@bot.tree.command(name="unmute", description="Unmute a user in the server")
@app_commands.describe(user="The user to unmute", reason="Reason for unmuting")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    await interaction.response.defer()
    
    try:
        # Remove timeout
        await user.timeout(None, reason=reason)
        
        # Remove mute role
        mute_role = discord.utils.get(interaction.guild.roles, name=Config.MUTE_ROLE_NAME)
        if mute_role:
            await user.remove_roles(mute_role, reason=reason)
        
        embed = discord.Embed(
            title="🔊 User Unmuted",
            description=f"{user.mention} has been unmuted",
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Log to logs channel
        logs_channel = bot.get_channel(Config.LOGS_CHANNEL_ID)
        if logs_channel:
            await logs_channel.send(embed=embed)
            
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to unmute this user.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

# Error handling
@ban.error
@softban.error
@kick.error
@mute.error
@unmute.error
async def command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    if not Config.DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables")
        exit(1)
    
    bot.run(Config.DISCORD_TOKEN)
