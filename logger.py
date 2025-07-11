import discord
from discord.ext import commands
import os
import asyncio
from datetime import datetime
from typing import Optional

class DiscordLogger:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID', '1387774689811628176'))
        self.log_channel = None
        
    async def get_log_channel(self) -> Optional[discord.TextChannel]:
        """Get the log channel"""
        if self.log_channel is None:
            try:
                self.log_channel = self.bot.get_channel(self.log_channel_id)
                if self.log_channel is None:
                    self.log_channel = await self.bot.fetch_channel(self.log_channel_id)
            except Exception as e:
                print(f"Error getting log channel: {e}")
                return None
        return self.log_channel
    
    async def log_event(self, event_type: str, description: str, color: int = 0x7289DA, 
                       user: Optional[discord.User] = None, guild: Optional[discord.Guild] = None,
                       channel: Optional[discord.TextChannel] = None):
        """Log an event to the Discord log channel"""
        try:
            log_channel = await self.get_log_channel()
            if not log_channel:
                return
            
            embed = discord.Embed(
                title=f"🌸 {event_type}",
                description=description,
                color=color,
                timestamp=datetime.utcnow()
            )
            
            # Add user information if provided
            if user:
                embed.add_field(
                    name="👤 User",
                    value=f"{user.display_name} ({user.name}#{user.discriminator})\nID: {user.id}",
                    inline=True
                )
            
            # Add guild information if provided
            if guild:
                embed.add_field(
                    name="🏠 Server",
                    value=f"{guild.name}\nID: {guild.id}",
                    inline=True
                )
            
            # Add channel information if provided
            if channel:
                embed.add_field(
                    name="📝 Channel",
                    value=f"#{channel.name}\nID: {channel.id}",
                    inline=True
                )
            
            embed.set_footer(text="Hinata Bot Logs")
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error logging event: {e}")
    
    async def log_startup(self):
        """Log bot startup"""
        await self.log_event(
            "Bot Started",
            f"Hinata has successfully started and is ready!\n"
            f"**Servers:** {len(self.bot.guilds)}\n"
            f"**Users:** {len(self.bot.users)}",
            color=0x00FF00
        )
    
    async def log_shutdown(self):
        """Log bot shutdown"""
        await self.log_event(
            "Bot Shutdown",
            "Hinata is shutting down...",
            color=0xFF0000
        )
    
    async def log_command_used(self, ctx, command_name: str, success: bool = True):
        """Log command usage"""
        color = 0x00FF00 if success else 0xFF0000
        status = "Success" if success else "Failed"
        
        await self.log_event(
            f"Command Used - {status}",
            f"**Command:** `{command_name}`\n"
            f"**Message:** {ctx.message.content[:100]}{'...' if len(ctx.message.content) > 100 else ''}",
            color=color,
            user=ctx.author,
            guild=ctx.guild,
            channel=ctx.channel
        )
    
    async def log_slash_command_used(self, interaction, command_name: str, success: bool = True):
        """Log slash command usage"""
        color = 0x00FF00 if success else 0xFF0000
        status = "Success" if success else "Failed"
        
        await self.log_event(
            f"Slash Command Used - {status}",
            f"**Command:** `/{command_name}`",
            color=color,
            user=interaction.user,
            guild=interaction.guild,
            channel=interaction.channel
        )
    
    async def log_image_generation(self, user, guild, channel, prompt: str, success: bool = True):
        """Log image generation attempts"""
        color = 0x00FF00 if success else 0xFF0000
        status = "Success" if success else "Failed"
        
        await self.log_event(
            f"Image Generation - {status}",
            f"**Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
            color=color,
            user=user,
            guild=guild,
            channel=channel
        )
    
    async def log_chat_response(self, user, guild, channel, message_content: str, response_length: int):
        """Log chat responses"""
        await self.log_event(
            "Chat Response",
            f"**User Message:** {message_content[:100]}{'...' if len(message_content) > 100 else ''}\n"
            f"**Response Length:** {response_length} characters",
            color=0x7289DA,
            user=user,
            guild=guild,
            channel=channel
        )
    
    async def log_channel_activation(self, user, guild, channel, activated: bool):
        """Log channel activation/deactivation"""
        action = "Activated" if activated else "Deactivated"
        color = 0x00FF00 if activated else 0xFF6B6B
        
        await self.log_event(
            f"Channel {action}",
            f"Hinata has been {action.lower()} in this channel.",
            color=color,
            user=user,
            guild=guild,
            channel=channel
        )
    
    async def log_mention_response(self, user, guild, channel, message_content: str):
        """Log when bot is mentioned"""
        await self.log_event(
            "Bot Mentioned",
            f"**Message:** {message_content[:150]}{'...' if len(message_content) > 150 else ''}",
            color=0xFFD700,
            user=user,
            guild=guild,
            channel=channel
        )
    
    async def log_error(self, error_type: str, error_message: str, user=None, guild=None, channel=None):
        """Log errors"""
        await self.log_event(
            f"Error - {error_type}",
            f"**Error:** {error_message[:300]}{'...' if len(error_message) > 300 else ''}",
            color=0xFF0000,
            user=user,
            guild=guild,
            channel=channel
        )
    
    async def log_guild_join(self, guild):
        """Log when bot joins a new guild"""
        await self.log_event(
            "Joined New Server",
            f"**Server Name:** {guild.name}\n"
            f"**Members:** {guild.member_count}\n"
            f"**Owner:** {guild.owner.display_name if guild.owner else 'Unknown'}",
            color=0x00FF00,
            guild=guild
        )
    
    async def log_guild_remove(self, guild):
        """Log when bot leaves a guild"""
        await self.log_event(
            "Left Server",
            f"**Server Name:** {guild.name}\n"
            f"**Members:** {guild.member_count}",
            color=0xFF6B6B,
            guild=guild
        )

async def setup(bot):
    """Setup function for the logger"""
    bot.discord_logger = DiscordLogger(bot)

