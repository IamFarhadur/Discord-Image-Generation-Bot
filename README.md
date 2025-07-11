# 🌸 Hinata - Discord Image Generation Bot

Hinata is a Discord bot that generates images from text prompts using the Pollinations.ai API. The bot supports multiple command types including slash commands, prefix commands, and mention-based commands.

## ✨ Features

- **Multiple Command Types:**
  - Slash commands (`/generate`)
  - Prefix commands (`%generate`, `%gen`, `%img`)
  - Mention commands (tag the bot with a prompt)
- **AI Image Generation** using Pollinations.ai API
- **Rich Embeds** with loading states and error handling
- **Customizable Prefix** (default: `%`)
- **Help Commands** for both slash and prefix formats

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Discord application and bot token
- Internet connection for API access

### Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "Hinata")
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Copy the bot token (you'll need this later)
6. Enable the following bot permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History

### Step 2: Invite the Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" > "URL Generator" section
2. Select the following scopes:
   - `bot`
   - `applications.commands`
3. Select the following bot permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Step 3: Install Dependencies

```bash
# Clone or download the bot files
cd hinata-discord-bot

# Install required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   COMMAND_PREFIX=%
   ```

### Step 5: Run the Bot

```bash
python bot.py
```

Or use the provided run script:
```bash
chmod +x run.sh
./run.sh
```

## 📖 Usage

### Slash Commands
- `/generate <prompt>` - Generate an image from a text prompt
- `/help` - Show help information

### Prefix Commands (default prefix: %)
- `%generate <prompt>` - Generate an image from a text prompt
- `%gen <prompt>` - Short alias for generate
- `%img <prompt>` - Another alias for generate
- `%help` - Show help information

### Mention Commands
- `@Hinata <prompt>` - Generate an image by mentioning the bot

### Example Prompts
- `a beautiful sunset over mountains`
- `a cute robot playing with cats`
- `cyberpunk city at night, neon lights`
- `watercolor painting of a forest`
- `anime girl with purple hair`
- `steampunk airship in the clouds`

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `COMMAND_PREFIX` | Command prefix for text commands | `%` |

### Customization

You can customize the bot by modifying the following files:
- `bot.py` - Main bot configuration and event handlers
- `commands.py` - Command implementations and help messages
- Change the bot's activity status in the `on_ready` event
- Modify embed colors and messages in the command functions

## 🔧 Troubleshooting

### Common Issues

1. **Bot doesn't respond to commands:**
   - Make sure the bot has the necessary permissions
   - Check that the bot token is correct in the `.env` file
   - Ensure the bot is online and connected

2. **Slash commands not working:**
   - Wait a few minutes after inviting the bot (slash commands need time to sync)
   - Try running the bot once to sync commands
   - Make sure the bot has "Use Slash Commands" permission

3. **Image generation fails:**
   - Check your internet connection
   - The Pollinations.ai API might be temporarily unavailable
   - Try with a different prompt

4. **Permission errors:**
   - Make sure the bot has "Send Messages" and "Embed Links" permissions
   - Check that the bot can see the channel you're using

### Debug Mode

To enable debug logging, you can modify the bot to include more detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 API Information

This bot uses the [Pollinations.ai](https://pollinations.ai/) API for image generation:
- **Endpoint:** `https://image.pollinations.ai/prompt/{prompt}`
- **Method:** GET request
- **Rate Limits:** Please be respectful with API usage
- **Image Format:** PNG/JPEG (automatically determined)

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source. The bot includes a footer crediting "©️ 2025 Hinata. All rights reserved" as requested.

## 🆘 Support

If you need help with setup or encounter any issues:
1. Check the troubleshooting section above
2. Make sure all dependencies are installed correctly
3. Verify your Discord bot token and permissions
4. Check the console output for error messages

---

**Made with ❤️ for the Discord community**

