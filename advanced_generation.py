import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import os
import io
import base64
from PIL import Image
import tempfile

class AdvancedGenerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        
        # API endpoints
        self.image_api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        self.video_api_url = "https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b"
        
        # Headers for API requests
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        
        # Fallback models if primary ones fail
        self.fallback_image_models = [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4"
        ]
        
        self.fallback_video_models = [
            "damo-vilab/text-to-video-ms-1.7b",
            "modelscope/text-to-video-synthesis"
        ]

    async def query_huggingface_api(self, api_url, payload, timeout=60):
        """Query Hugging Face API with error handling and retries"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(api_url, headers=self.headers, json=payload, timeout=timeout)
            )
            
            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                # Model is loading, wait and retry
                await asyncio.sleep(10)
                response = await loop.run_in_executor(
                    None, 
                    lambda: requests.post(api_url, headers=self.headers, json=payload, timeout=timeout)
                )
                if response.status_code == 200:
                    return response.content
            
            return None
            
        except Exception as e:
            print(f"API request error: {e}")
            return None

    async def generate_advanced_image(self, prompt, negative_prompt=None, width=1024, height=1024):
        """Generate image using Hugging Face API"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }
        }
        
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt
        
        # Try primary model first
        image_bytes = await self.query_huggingface_api(self.image_api_url, payload)
        
        # Try fallback models if primary fails
        if not image_bytes:
            for fallback_model in self.fallback_image_models:
                fallback_url = f"https://api-inference.huggingface.co/models/{fallback_model}"
                image_bytes = await self.query_huggingface_api(fallback_url, payload)
                if image_bytes:
                    break
        
        return image_bytes

    async def generate_advanced_video(self, prompt, num_frames=16):
        """Generate video using Hugging Face API"""
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_frames": num_frames,
                "num_inference_steps": 25
            }
        }
        
        # Try primary model first
        video_bytes = await self.query_huggingface_api(self.video_api_url, payload, timeout=120)
        
        # Try fallback models if primary fails
        if not video_bytes:
            for fallback_model in self.fallback_video_models:
                fallback_url = f"https://api-inference.huggingface.co/models/{fallback_model}"
                video_bytes = await self.query_huggingface_api(fallback_url, payload, timeout=120)
                if video_bytes:
                    break
        
        return video_bytes

    @app_commands.command(name="imgen", description="Generate high-quality images using advanced AI models")
    @app_commands.describe(
        prompt="The text prompt to generate an image from",
        negative_prompt="What to avoid in the image (optional)",
        size="Image size preset"
    )
    @app_commands.choices(size=[
        app_commands.Choice(name="Square (1024x1024)", value="1024x1024"),
        app_commands.Choice(name="Portrait (768x1024)", value="768x1024"),
        app_commands.Choice(name="Landscape (1024x768)", value="1024x768"),
        app_commands.Choice(name="Wide (1280x720)", value="1280x720")
    ])
    async def slash_imgen(self, interaction: discord.Interaction, prompt: str, negative_prompt: str = None, size: str = "1024x1024"):
        """Advanced image generation slash command"""
        await interaction.response.defer()
        
        # Log command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_slash_command_used(interaction, "imgen", True)
        
        if not self.hf_token:
            embed = discord.Embed(
                title="❌ Configuration Error",
                description="Hugging Face token is not configured. Please set HUGGINGFACE_TOKEN in environment variables.",
                color=0xFF0000
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await interaction.followup.send(embed=embed)
            return
        
        # Parse size
        width, height = map(int, size.split('x'))
        
        # Create loading embed
        loading_embed = discord.Embed(
            title="🎨 Generating Advanced Image...",
            description=f"**Prompt:** {prompt}\n"
                       f"**Size:** {size}\n"
                       f"**Negative Prompt:** {negative_prompt or 'None'}\n\n"
                       "Using advanced AI models... This may take a moment.",
            color=0x9B59B6
        )
        loading_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        
        await interaction.followup.send(embed=loading_embed)
        
        try:
            # Generate image
            image_bytes = await self.generate_advanced_image(prompt, negative_prompt, width, height)
            
            if image_bytes:
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(image_bytes)
                    temp_file_path = temp_file.name
                
                # Create success embed
                success_embed = discord.Embed(
                    title="✨ Advanced Image Generated!",
                    description=f"**Prompt:** {prompt}\n**Size:** {size}",
                    color=0x00FF00
                )
                success_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
                
                # Send image as file
                with open(temp_file_path, 'rb') as f:
                    file = discord.File(f, filename=f"hinata_imgen_{interaction.id}.png")
                    await interaction.edit_original_response(embed=success_embed, attachments=[file])
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                # Log successful generation
                if self.bot.discord_logger:
                    await self.bot.discord_logger.log_image_generation(
                        interaction.user, interaction.guild, interaction.channel, prompt, True
                    )
            else:
                raise Exception("Failed to generate image")
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Generation Failed",
                description=f"Sorry, I couldn't generate an advanced image for: **{prompt}**\n\n"
                           "The AI models might be busy. Please try again later.",
                color=0xFF0000
            )
            error_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            
            await interaction.edit_original_response(embed=error_embed)
            
            # Log failed generation
            if self.bot.discord_logger:
                await self.bot.discord_logger.log_image_generation(
                    interaction.user, interaction.guild, interaction.channel, prompt, False
                )

    @app_commands.command(name="vidgen", description="Generate videos from text using AI")
    @app_commands.describe(
        prompt="The text prompt to generate a video from",
        duration="Video duration (affects number of frames)"
    )
    @app_commands.choices(duration=[
        app_commands.Choice(name="Short (2-3 seconds)", value="16"),
        app_commands.Choice(name="Medium (4-5 seconds)", value="24"),
        app_commands.Choice(name="Long (6-8 seconds)", value="32")
    ])
    async def slash_vidgen(self, interaction: discord.Interaction, prompt: str, duration: str = "16"):
        """Video generation slash command"""
        await interaction.response.defer()
        
        # Check if user has video generation access
        embed = discord.Embed(
            title="🎬 Video Generation - Premium Feature",
            description="Video generation is a premium feature that requires an upgraded subscription.\n\n"
                       "**What you get with video generation:**\n"
                       "• AI-powered text-to-video creation\n"
                       "• Multiple duration options\n"
                       "• High-quality video output\n"
                       "• Advanced AI models\n\n"
                       "Please upgrade your subscription to unlock this feature!",
            color=0xFFD700
        )
        embed.add_field(
            name="Alternative",
            value="You can still use our free image generation features:\n"
                  "• `/generate` - Basic image generation\n"
                  "• `/imgen` - Advanced image generation",
            inline=False
        )
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        
        await interaction.followup.send(embed=embed)

    @commands.command(name="imgen", aliases=["advimg", "hqimg"])
    async def prefix_imgen(self, ctx, *, prompt: str = None):
        """Advanced image generation prefix command"""
        # Log command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_command_used(ctx, f"imgen {prompt or ''}", True)
        
        if not prompt or not prompt.strip():
            embed = discord.Embed(
                title="❌ Error",
                description=f"Please provide a prompt for advanced image generation!\n\n"
                           f"**Usage:** `{ctx.prefix}imgen <prompt>`\n"
                           f"**Example:** `{ctx.prefix}imgen a majestic dragon in a fantasy landscape`",
                color=0xFF0000
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await ctx.send(embed=embed)
            return
        
        if not self.hf_token:
            embed = discord.Embed(
                title="❌ Configuration Error",
                description="Hugging Face token is not configured. Please set HUGGINGFACE_TOKEN in environment variables.",
                color=0xFF0000
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await ctx.send(embed=embed)
            return
        
        # Create loading embed
        loading_embed = discord.Embed(
            title="🎨 Generating Advanced Image...",
            description=f"**Prompt:** {prompt}\n\n"
                       "Using advanced AI models... This may take a moment.",
            color=0x9B59B6
        )
        loading_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        
        loading_message = await ctx.send(embed=loading_embed)
        
        try:
            # Generate image with default settings
            image_bytes = await self.generate_advanced_image(prompt)
            
            if image_bytes:
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(image_bytes)
                    temp_file_path = temp_file.name
                
                # Create success embed
                success_embed = discord.Embed(
                    title="✨ Advanced Image Generated!",
                    description=f"**Prompt:** {prompt}",
                    color=0x00FF00
                )
                success_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
                
                # Send image as file
                with open(temp_file_path, 'rb') as f:
                    file = discord.File(f, filename=f"hinata_imgen_{ctx.message.id}.png")
                    await loading_message.edit(embed=success_embed, attachments=[file])
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                # Log successful generation
                if self.bot.discord_logger:
                    await self.bot.discord_logger.log_image_generation(
                        ctx.author, ctx.guild, ctx.channel, prompt, True
                    )
            else:
                raise Exception("Failed to generate image")
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Generation Failed",
                description=f"Sorry, I couldn't generate an advanced image for: **{prompt}**\n\n"
                           "The AI models might be busy. Please try again later.",
                color=0xFF0000
            )
            error_embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            
            await loading_message.edit(embed=error_embed)
            
            # Log failed generation
            if self.bot.discord_logger:
                await self.bot.discord_logger.log_image_generation(
                    ctx.author, ctx.guild, ctx.channel, prompt, False
                )

    @commands.command(name="vidgen", aliases=["video", "genvid"])
    async def prefix_vidgen(self, ctx, *, prompt: str = None):
        """Video generation prefix command"""
        # Log command usage
        if self.bot.discord_logger:
            await self.bot.discord_logger.log_command_used(ctx, f"vidgen {prompt or ''}", True)
        
        if not prompt or not prompt.strip():
            embed = discord.Embed(
                title="❌ Error",
                description=f"Please provide a prompt for video generation!\n\n"
                           f"**Usage:** `{ctx.prefix}vidgen <prompt>`\n"
                           f"**Example:** `{ctx.prefix}vidgen a cat playing with a ball`",
                color=0xFF0000
            )
            embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
            await ctx.send(embed=embed)
            return
        
        # Show premium feature message
        embed = discord.Embed(
            title="🎬 Video Generation - Premium Feature",
            description="Video generation is a premium feature that requires an upgraded subscription.\n\n"
                       "**What you get with video generation:**\n"
                       "• AI-powered text-to-video creation\n"
                       "• Multiple duration options\n"
                       "• High-quality video output\n"
                       "• Advanced AI models\n\n"
                       "Please upgrade your subscription to unlock this feature!",
            color=0xFFD700
        )
        embed.add_field(
            name="Alternative",
            value="You can still use our free image generation features:\n"
                  f"• `{ctx.prefix}generate` - Basic image generation\n"
                  f"• `{ctx.prefix}imgen` - Advanced image generation",
            inline=False
        )
        embed.set_footer(text="©️ 2025 Hinata. All rights reserved")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedGenerationCommands(bot))

