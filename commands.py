import discord
from discord.ext import commands
from discord import app_commands
import urllib.parse
import requests
import asyncio

class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="generate", description="Generate an image from a text prompt")
    @app_commands.describe(prompt="The text prompt to generate an image from")
    async def slash_generate(self, interaction: discord.Interaction, prompt: str):
        """Slash command for image generation"""
        await interaction.response.defer()
        
        # Log slash command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_slash_command_used(interaction, "generate", True)
        
        if not prompt or not prompt.strip():
            embed = discord.Embed(
                title="❌ Error",
                description="Please provide a prompt for image generation!",
                color=0xFF0000
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await interaction.followup.send(embed=embed)
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
        
        await interaction.followup.send(embed=loading_embed)
        
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
                
                await interaction.edit_original_response(embed=success_embed)
                
                # Log successful image generation
                if self.bot.discord_logger:
                    await self.bot.discord_logger.log_image_generation(
                        interaction.user, interaction.guild, interaction.channel, clean_prompt, True
                    )
            else:
                raise Exception(f"HTTP {response.status_code}")
                        
        except Exception as e:
            # Create error embed
            error_embed = discord.Embed(
                title="❌ Generation Failed",
                description=f"Sorry, I couldn\'t generate an image for: **{clean_prompt}**\n\n"
                           "Please try again with a different prompt.",
                color=0xFF0000
            )
            error_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            
            await interaction.edit_original_response(embed=error_embed)
            
            # Log failed image generation
            if self.bot.discord_logger:
                await self.bot.discord_logger.log_image_generation(
                    interaction.user, interaction.guild, interaction.channel, clean_prompt, False
                )

    @commands.command(name="generate", aliases=["gen", "img", "image"])
    async def prefix_generate(self, ctx, *, prompt: str = None):
        """Prefix command for image generation"""
        # Log command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_command_used(ctx, f"generate {prompt or ''}", True)
        
        if not prompt or not prompt.strip():
            embed = discord.Embed(
                title="❌ Error",
                description=f"Please provide a prompt for image generation!\n\n"
                           f"**Usage:** `{ctx.prefix}generate <prompt>`\n"
                           f"**Example:** `{ctx.prefix}generate a cute cat`",
                color=0xFF0000
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await ctx.send(embed=embed)
            return
        
        await self.bot.generate_image_from_prompt(ctx, prompt)

    @commands.command(name="help", aliases=["h", "commands"])
    async def help_command(self, ctx):
        """Show help information"""
        # Log command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_command_used(ctx, "help", True)
        
        embed = discord.Embed(
            title="🌸 Hinata - AI Assistant Bot",
            description="I can generate images, videos, and chat with you using AI!",
            color=0x7289DA
        )
        
        embed.add_field(
            name="📝 Slash Commands",
            value="`/generate <prompt>` - Generate an image\n"
                  "`/imgen <prompt>` - Advanced image generation\n"
                  "`/vidgen <prompt>` - Video generation (Premium)\n"
                  "`/activate` - Activate chat mode in this channel\n"
                  "`/deactivate` - Deactivate chat mode\n"
                  "`/help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Prefix Commands",
            value=f"`{ctx.prefix}generate <prompt>` - Generate an image\n"
                  f"`{ctx.prefix}gen <prompt>` - Generate an image (short)\n"
                  f"`{ctx.prefix}img <prompt>` - Generate an image (alias)\n"
                  f"`{ctx.prefix}imgen <prompt>` - Advanced image generation\n"
                  f"`{ctx.prefix}vidgen <prompt>` - Video generation (Premium)\n"
                  f"`{ctx.prefix}activate` - Activate chat mode\n"
                  f"`{ctx.prefix}deactivate` - Deactivate chat mode\n"
                  f"`{ctx.prefix}status` - Check channel status\n"
                  f"`{ctx.prefix}help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="💬 Chat & Mention Commands",
            value=f"• Mention me for chat: `@{self.bot.user.display_name} Hello!`\n"
                  f"• Mention me for images: `@{self.bot.user.display_name} draw a cat`\n"
                  f"• Activate chat mode to talk without mentions!",
            inline=False
        )
        
        embed.add_field(
            name="📖 Generation Examples",
            value="**Basic Images:**\n"
                  "• `a beautiful sunset over mountains`\n"
                  "• `a cute robot playing with cats`\n\n"
                  "**Advanced Images:**\n"
                  "• `photorealistic portrait of a wizard`\n"
                  "• `cyberpunk city at night, neon lights`\n\n"
                  "**Videos (Premium):**\n"
                  "• `a cat chasing a butterfly in a garden`\n"
                  "• `waves crashing on a rocky shore`",
            inline=False
        )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await ctx.send(embed=embed)

    @app_commands.command(name="help", description="Show help information about Hinata")
    async def slash_help(self, interaction: discord.Interaction):
        """Slash command for help"""
        # Log slash command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_slash_command_used(interaction, "help", True)
        
        embed = discord.Embed(
            title="🌸 Hinata - AI Assistant Bot",
            description="I can generate images, videos, and chat with you using AI!",
            color=0x7289DA
        )
        
        embed.add_field(
            name="📝 Slash Commands",
            value="`/generate <prompt>` - Generate an image\n"
                  "`/imgen <prompt>` - Advanced image generation\n"
                  "`/vidgen <prompt>` - Video generation (Premium)\n"
                  "`/activate` - Activate chat mode in this channel\n"
                  "`/deactivate` - Deactivate chat mode\n"
                  "`/help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Prefix Commands",
            value=f"`%generate <prompt>` - Generate an image\n"
                  f"`%gen <prompt>` - Generate an image (short)\n"
                  f"`%img <prompt>` - Generate an image (alias)\n"
                  f"`%imgen <prompt>` - Advanced image generation\n"
                  f"`%vidgen <prompt>` - Video generation (Premium)\n"
                  f"`%activate` - Activate chat mode\n"
                  f"`%deactivate` - Deactivate chat mode\n"
                  f"`%status` - Check channel status\n"
                  f"`%help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="💬 Chat & Mention Commands",
            value=f"• Mention me for chat: `@{self.bot.user.display_name} Hello!`\n"
                  f"• Mention me for images: `@{self.bot.user.display_name} draw a cat`\n"
                  f"• Activate chat mode to talk without mentions!",
            inline=False
        )
        
        embed.add_field(
            name="📖 Generation Examples",
            value="**Basic Images:**\n"
                  "• `a beautiful sunset over mountains`\n"
                  "• `a cute robot playing with cats`\n\n"
                  "**Advanced Images:**\n"
                  "• `photorealistic portrait of a wizard`\n"
                  "• `cyberpunk city at night, neon lights`\n\n"
                  "**Videos (Premium):**\n"
                  "• `a cat chasing a butterfly in a garden`\n"
                  "• `waves crashing on a rocky shore`",
            inline=False
        )
        
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ImageCommands(bot))

