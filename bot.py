import discord
from discord.ext import commands
import os
import asyncio
import requests
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "%")

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class HinataBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.discord_logger = None
        self.chat_manager = None
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        print(f"Setting up {self.user} (ID: {self.user.id})")
        
        # Load logger extension first
        try:
            await self.load_extension("logger")
            print("Loaded logger extension")
        except Exception as e:
            print(f"Failed to load logger: {e}")
        
        # Load commands cog
        try:
            await self.load_extension("commands")
            print("Loaded commands extension")
        except Exception as e:
            print(f"Failed to load commands: {e}")
        
        # Load chat cog
        try:
            await self.load_extension("chat")
            print("Loaded chat extension")
            # Get chat manager reference
            chat_cog = self.get_cog("ChatCommands")
            if chat_cog:
                self.chat_manager = chat_cog.chat_manager
        except Exception as e:
            print(f"Failed to load chat: {e}")
        
        # Load advanced generation cog
        try:
            await self.load_extension("advanced_generation")
            print("Loaded advanced generation extension")
        except Exception as e:
            print(f"Failed to load advanced generation: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        print(f"{self.user} has awakened! 🌸")
        print(f"Bot ID: {self.user.id}")
        print(f"Prefix: {PREFIX}")
        print("---")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for messages and image requests | /help"
        )
        await self.change_presence(activity=activity)
        
        # Log startup
        if self.discord_logger:
            await self.discord_logger.log_startup()

    async def on_message(self, message):
        """Handle messages for mentions, chat responses, and prefix commands"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Check if bot is mentioned
        if self.user in message.mentions:
            await self.handle_mention(message)
            return
        
        # Check if channel is active for chat
        if self.chat_manager and self.chat_manager.is_channel_active(message.channel.id):
            await self.handle_chat_message(message)
            return
            
        # Process commands normally
        await self.process_commands(message)
    
    async def handle_mention(self, message):
        """Handle when the bot is mentioned"""
        # Log the mention
        if self.discord_logger:
            await self.discord_logger.log_mention_response(
                message.author, message.guild, message.channel, message.content
            )
        
        # Extract the prompt from the message (remove the mention)
        content = message.content
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "")
        
        prompt = content.strip()
        
        if not prompt:
            embed = discord.Embed(
                title="Hi there! 👋",
                description="I'm Hinata, your friendly assistant!\n\n"
                           "**How to use me:**\n"
                           f"• **Chat:** Mention me with a message or use `/activate` in a channel\n"
                           f"• **Images:** Mention me with a prompt: `@{self.user.display_name} a cute cat`\n"
                           f"• **Slash commands:** `/generate`, `/activate`, `/help`\n"
                           f"• **Prefix commands:** `{PREFIX}generate`, `{PREFIX}activate`, `{PREFIX}help`",
                color=0x7289DA
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await message.reply(embed=embed)
            return
        
        # Check if this looks like an image generation request
        image_keywords = ["generate", "create", "make", "draw", "image", "picture", "art", "painting"]
        is_image_request = any(keyword in prompt.lower() for keyword in image_keywords)
        
        if is_image_request or len(prompt.split()) > 10:  # Long prompts are likely image requests
            # Generate image for the mentioned prompt
            await self.generate_image_from_prompt(message, prompt, is_mention=True)
        else:
            # Generate chat response
            if self.chat_manager:
                await self.handle_chat_response(message, prompt)
            else:
                # Fallback if chat is not available
                await self.generate_image_from_prompt(message, prompt, is_mention=True)
    
    async def handle_chat_message(self, message):
        """Handle chat messages in active channels"""
        if not self.chat_manager:
            return
        
        # Generate chat response
        await self.handle_chat_response(message, message.content)
    
    async def handle_chat_response(self, message, content):
        """Generate and send a chat response"""
        try:
            # Show typing indicator
            async with message.channel.typing():
                response = await self.chat_manager.generate_chat_response(
                    content, message.channel.id, message.author.display_name
                )
            
            if response:
                await message.reply(response)
                
                # Log the chat response
                if self.discord_logger:
                    await self.discord_logger.log_chat_response(
                        message.author, message.guild, message.channel, 
                        content, len(response)
                    )
        except Exception as e:
            print(f"Error handling chat response: {e}")
            if self.discord_logger:
                await self.discord_logger.log_error(
                    "Chat Response", str(e), 
                    message.author, message.guild, message.channel
                )
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild"""
        if self.discord_logger:
            await self.discord_logger.log_guild_join(guild)
    
    async def on_guild_remove(self, guild):
        """Called when the bot leaves a guild"""
        if self.discord_logger:
            await self.discord_logger.log_guild_remove(guild)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if self.discord_logger:
            await self.discord_logger.log_error(
                "Command Error", str(error),
                ctx.author, ctx.guild, ctx.channel
            )
        
        # Send user-friendly error message
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        embed = discord.Embed(
            title="❌ Oops!",
            description="Something went wrong while processing your command. Please try again!",
            color=0xFF0000
        )
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await ctx.send(embed=embed)

# Create bot instance
bot = HinataBot()

async def generate_image_from_prompt(ctx_or_message, prompt: str, is_mention: bool = False):
    """Generate image from prompt using pollinations.ai API"""
    if not prompt or not prompt.strip():
        embed = discord.Embed(
            title="❌ Error",
            description="Please provide a prompt for image generation!",
            color=0xFF0000
        )
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        
        if is_mention:
            await ctx_or_message.reply(embed=embed)
        else:
            await ctx_or_message.send(embed=embed)
        return
    
    # Clean and encode the prompt
    clean_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    
    # Create the image URL
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    # Create loading embed
    loading_embed = discord.Embed(
        title="🎨 Generating Image...",
        description=f"**Prompt:** {clean_prompt}\n\nPlease wait while I create your image...",
        color=0xFFD700
    )
    loading_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
    
    if is_mention:
        loading_message = await ctx_or_message.reply(embed=loading_embed)
    else:
        loading_message = await ctx_or_message.send(embed=loading_embed)
    
    try:
        # Use requests for synchronous HTTP call, run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.get(image_url, stream=True))
        
        if response.status_code == 200:
            # Create success embed
            success_embed = discord.Embed(
                title="✨ Image Generated!",
                description=f"**Prompt:** {clean_prompt}",
                color=0x00FF00
            )
            success_embed.set_image(url=image_url)
            success_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            
            await loading_message.edit(embed=success_embed)
            
            # Log successful image generation
            if bot.discord_logger:
                user = ctx_or_message.author if hasattr(ctx_or_message, "author") else ctx_or_message.user
                guild = ctx_or_message.guild
                channel = ctx_or_message.channel
                await bot.discord_logger.log_image_generation(
                    user, guild, channel, clean_prompt, True
                )
        else:
            raise Exception(f"HTTP {response.status_code}")
            
    except Exception as e:
        # Create error embed
        error_embed = discord.Embed(
            title="❌ Generation Failed",
            description=f"Sorry, I couldn't generate an image for: **{clean_prompt}**\n\n"
                       "Please try again with a different prompt.",
            color=0xFF0000
        )
        error_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        
        await loading_message.edit(embed=error_embed)
        
        # Log failed image generation
        if bot.discord_logger:
            user = ctx_or_message.author if hasattr(ctx_or_message, "author") else ctx_or_message.user
            guild = ctx_or_message.guild
            channel = ctx_or_message.channel
            await bot.discord_logger.log_image_generation(
                user, guild, channel, clean_prompt, False
            )

# Add the function to bot class
bot.generate_image_from_prompt = generate_image_from_prompt

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Error: Invalid Discord token!")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")


