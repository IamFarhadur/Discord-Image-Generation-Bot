import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from openai import OpenAI
import json
from typing import Dict, List, Optional

class ChatManager:
    def __init__(self, bot):
        self.bot = bot
        self.openrouter_client = None
        self.active_channels: Dict[int, bool] = {}  # channel_id -> is_active
        self.conversation_history: Dict[int, List[Dict]] = {}  # channel_id -> messages
        self.max_history_length = 10  # Keep last 10 messages for context
        
        # Initialize OpenRouter client
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
        
    def is_channel_active(self, channel_id: int) -> bool:
        """Check if Hinata is active in a channel"""
        return self.active_channels.get(channel_id, False)
    
    def activate_channel(self, channel_id: int):
        """Activate Hinata in a channel"""
        self.active_channels[channel_id] = True
        # Initialize conversation history for this channel
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []
    
    def deactivate_channel(self, channel_id: int):
        """Deactivate Hinata in a channel"""
        self.active_channels[channel_id] = False
        # Clear conversation history when deactivated
        if channel_id in self.conversation_history:
            del self.conversation_history[channel_id]
    
    def add_to_conversation(self, channel_id: int, role: str, content: str):
        """Add a message to the conversation history"""
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []
        
        self.conversation_history[channel_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only the last N messages to prevent context overflow
        if len(self.conversation_history[channel_id]) > self.max_history_length:
            self.conversation_history[channel_id] = self.conversation_history[channel_id][-self.max_history_length:]
    
    def get_conversation_history(self, channel_id: int) -> List[Dict]:
        """Get conversation history for a channel"""
        return self.conversation_history.get(channel_id, [])
    
    async def generate_chat_response(self, message_content: str, channel_id: int, user_name: str) -> Optional[str]:
        """Generate a chat response using OpenRouter"""
        if not self.openrouter_client:
            return "Sorry, I'm not configured for chat yet. Please set up the OpenRouter API key!"
        
        try:
            # Add user message to conversation history
            self.add_to_conversation(channel_id, "user", f"{user_name}: {message_content}")
            
            # Get conversation history
            history = self.get_conversation_history(channel_id)
            
            # Prepare messages for the API
            system_message = {
                "role": "system",
                "content": "You are Hinata, a friendly and helpful Discord bot. You are cheerful, supportive, and love to help users. You can generate images and chat with users. Keep your responses conversational and engaging, but not too long. Use emojis occasionally to show personality. You are in a Discord server, so keep responses appropriate for a community setting."
            }
            
            messages = [system_message] + history
            
            # Make API call to OpenRouter
            completion = self.openrouter_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://discord.com",
                    "X-Title": "Hinata Discord Bot",
                },
                model="google/gemma-3n-e4b-it:free",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            response = completion.choices[0].message.content
            
            # Add bot response to conversation history
            self.add_to_conversation(channel_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "Sorry, I'm having trouble thinking right now. Please try again later! 😅"

class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chat_manager = ChatManager(bot)
        
    @app_commands.command(name="activate", description="Activate Hinata in this channel for automatic responses")
    async def slash_activate(self, interaction: discord.Interaction):
        """Slash command to activate Hinata in a channel"""
        channel_id = interaction.channel.id
        
        if self.chat_manager.is_channel_active(channel_id):
            embed = discord.Embed(
                title="🌸 Already Active!",
                description="I'm already active in this channel! I'll respond to all messages here.",
                color=0xFFD700
            )
        else:
            self.chat_manager.activate_channel(channel_id)
            embed = discord.Embed(
                title="🌸 Hinata Activated!",
                description="I'm now active in this channel! I'll respond to all messages here.\n\n"
                           "Use `/deactivate` to turn off automatic responses.",
                color=0x00FF00
            )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="deactivate", description="Deactivate Hinata in this channel")
    async def slash_deactivate(self, interaction: discord.Interaction):
        """Slash command to deactivate Hinata in a channel"""
        channel_id = interaction.channel.id
        
        if not self.chat_manager.is_channel_active(channel_id):
            embed = discord.Embed(
                title="🌸 Already Inactive",
                description="I'm not active in this channel. I only respond when mentioned.",
                color=0xFFD700
            )
        else:
            self.chat_manager.deactivate_channel(channel_id)
            embed = discord.Embed(
                title="🌸 Hinata Deactivated",
                description="I'm no longer active in this channel. I'll only respond when mentioned now.\n\n"
                           "Use `/activate` to turn on automatic responses again.",
                color=0xFF6B6B
            )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name="activate", aliases=["active", "on"])
    async def prefix_activate(self, ctx):
        """Prefix command to activate Hinata in a channel"""
        channel_id = ctx.channel.id
        
        # Log command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_command_used(ctx, "activate", True)
        
        if self.chat_manager.is_channel_active(channel_id):
            embed = discord.Embed(
                title="🌸 Already Active!",
                description="I'm already active in this channel! I'll respond to all messages here.",
                color=0xFFD700
            )
        else:
            self.chat_manager.activate_channel(channel_id)
            embed = discord.Embed(
                title="🌸 Hinata Activated!",
                description=f"I'm now active in this channel! I'll respond to all messages here.\n\n"
                           f"Use `{ctx.prefix}deactivate` to turn off automatic responses.",
                color=0x00FF00
            )
            
            # Log channel activation
            if self.bot.discord_logger:
                await self.bot.discord_logger.log_channel_activation(
                    ctx.author, ctx.guild, ctx.channel, True
                )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await ctx.send(embed=embed)
    
    @commands.command(name="deactivate", aliases=["inactive", "off"])
    async def prefix_deactivate(self, ctx):
        """Prefix command to deactivate Hinata in a channel"""
        channel_id = ctx.channel.id
        
        if not self.chat_manager.is_channel_active(channel_id):
            embed = discord.Embed(
                title="🌸 Already Inactive",
                description="I'm not active in this channel. I only respond when mentioned.",
                color=0xFFD700
            )
        else:
            self.chat_manager.deactivate_channel(channel_id)
            embed = discord.Embed(
                title="🌸 Hinata Deactivated",
                description=f"I'm no longer active in this channel. I'll only respond when mentioned now.\n\n"
                           f"Use `{ctx.prefix}activate` to turn on automatic responses again.",
                color=0xFF6B6B
            )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await ctx.send(embed=embed)
    
    @commands.command(name="status", aliases=["state"])
    async def chat_status(self, ctx):
        """Check if Hinata is active in the current channel"""
        channel_id = ctx.channel.id
        is_active = self.chat_manager.is_channel_active(channel_id)
        
        if is_active:
            embed = discord.Embed(
                title="🌸 Channel Status: Active",
                description="I'm currently active in this channel and will respond to all messages!",
                color=0x00FF00
            )
        else:
            embed = discord.Embed(
                title="🌸 Channel Status: Inactive",
                description="I'm currently inactive in this channel. I only respond when mentioned.",
                color=0xFF6B6B
            )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChatCommands(bot))

