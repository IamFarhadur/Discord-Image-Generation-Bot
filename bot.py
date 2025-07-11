import discord
from discord.ext import commands
import os
import asyncio
import aiohttp
import requests
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', '%')

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
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        print(f"Setting up {self.user} (ID: {self.user.id})")
        
        # Load commands cog
        try:
            await self.load_extension('commands')
            print("Loaded commands extension")
        except Exception as e:
            print(f"Failed to load commands: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        print(f'{self.user} has awakened! 🌸')
        print(f'Bot ID: {self.user.id}')
        print(f'Prefix: {PREFIX}')
        print('---')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for image requests | /generate or %generate"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        """Handle messages for mentions and prefix commands"""
        # Ignore messages from bots
        if message.author.bot:
            return
            
        # Check if bot is mentioned
        if self.user in message.mentions:
            await self.handle_mention(message)
            return
            
        # Process commands normally
        await self.process_commands(message)
    
    async def handle_mention(self, message):
        """Handle when the bot is mentioned"""
        # Extract the prompt from the message (remove the mention)
        content = message.content
        for mention in message.mentions:
            content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
        
        prompt = content.strip()
        
        if not prompt:
            embed = discord.Embed(
                title="Hi there! 👋",
                description="I'm Hinata, your image generation assistant!\n\n"
                           "**How to use me:**\n"
                           f"• Mention me with a prompt: `@{self.user.display_name} a cute cat`\n"
                           f"• Use slash command: `/generate prompt:a cute cat`\n"
                           f"• Use prefix command: `{PREFIX}generate a cute cat`",
                color=0x7289DA
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await message.reply(embed=embed)
            return
            
        # Generate image for the mentioned prompt
        await self.generate_image_from_prompt(message, prompt, is_mention=True)

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
        # Test if the image URL is accessible
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    # Create success embed
                    success_embed = discord.Embed(
                        title="✨ Image Generated!",
                        description=f"**Prompt:** {clean_prompt}",
                        color=0x00FF00
                    )
                    success_embed.set_image(url=image_url)
                    success_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
                    
                    await loading_message.edit(embed=success_embed)
                else:
                    raise Exception(f"HTTP {response.status}")
                    
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

