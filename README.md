# 🌸 Hinata - Discord AI Assistant Bot

Hinata is a powerful Discord bot that combines AI image generation and intelligent chat capabilities. She can generate images from text prompts using the Pollinations.ai API and engage in conversations using Google's Gemma model through OpenRouter. The bot supports multiple command types and includes comprehensive logging features.

## ✨ Features

### 🎨 Image Generation
- **AI Image Generation** using Pollinations.ai API
- **Multiple Command Types:**
  - Slash commands (`/generate`)
  - Prefix commands (`%generate`, `%gen`, `%img`)
  - Mention commands (tag the bot with a prompt)

### 💬 AI Chat
- **Intelligent Conversations** using Google Gemma 3n model via OpenRouter
- **Channel Activation System** - activate Hinata in channels for automatic responses
- **Context-Aware** - maintains conversation history for natural dialogue
- **Smart Detection** - automatically detects image vs chat requests when mentioned

### 📊 Logging & Monitoring
- **Comprehensive Logging** to a designated Discord channel
- **Event Tracking** - commands, image generation, chat responses, errors
- **Server Analytics** - guild joins/leaves, user interactions
- **Real-time Monitoring** - all bot activities are logged with detailed information

### 🛠️ Command System
- **Rich Embeds** with loading states and error handling
- **Customizable Prefix** (default: `%`)
- **Help Commands** for both slash and prefix formats
- **Error Handling** with user-friendly messages

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Discord application and bot token
- OpenRouter API key (for chat features)
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

### Step 2: Get OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the API key (you'll need this for chat features)

### Step 3: Invite the Bot to Your Server

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

### Step 4: Install Dependencies

```bash
# Clone or download the bot files
cd hinata-discord-bot

# Install required packages
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your tokens:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   COMMAND_PREFIX=%
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   LOG_CHANNEL_ID=1387774689811628176
   ```

### Step 6: Run the Bot

```bash
python bot.py
```

Or use the provided run script:
```bash
chmod +x run.sh
./run.sh
```

## 📖 Usage

### 🎨 Image Generation

#### Slash Commands
- `/generate <prompt>` - Generate an image from a text prompt

#### Prefix Commands (default prefix: %)
- `%generate <prompt>` - Generate an image from a text prompt
- `%gen <prompt>` - Short alias for generate
- `%img <prompt>` - Another alias for generate

#### Mention Commands
- `@Hinata draw a cute cat` - Generate an image by mentioning the bot

### 💬 Chat Features

#### Channel Activation
- `/activate` or `%activate` - Activate Hinata in the current channel
- `/deactivate` or `%deactivate` - Deactivate Hinata in the current channel
- `%status` - Check if Hinata is active in the current channel

#### Chat Interaction
- **In Active Channels:** Just type normally, Hinata will respond to all messages
- **Mention Chat:** `@Hinata Hello! How are you?` - Chat by mentioning the bot
- **Smart Detection:** Hinata automatically detects if you want to chat or generate images

### 🆘 Help Commands
- `/help` or `%help` - Show comprehensive help information

### 📖 Example Prompts

#### Image Generation
- `a beautiful sunset over mountains`
- `a cute robot playing with cats`
- `cyberpunk city at night, neon lights`
- `watercolor painting of a forest`
- `anime girl with purple hair`
- `steampunk airship in the clouds`

#### Chat Examples
- `@Hinata What's the weather like today?`
- `@Hinata Tell me a joke!`
- `@Hinata Help me brainstorm ideas for a project`

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | - | Yes |
| `OPENROUTER_API_KEY` | Your OpenRouter API key | - | Yes (for chat) |
| `COMMAND_PREFIX` | Command prefix for text commands | `%` | No |
| `LOG_CHANNEL_ID` | Discord channel ID for logging | `1387774689811628176` | No |

### Customization

You can customize the bot by modifying the following files:
- `bot.py` - Main bot configuration and event handlers
- `commands.py` - Image generation command implementations
- `chat.py` - Chat functionality and channel management
- `logger.py` - Logging system configuration
- Change the bot's activity status in the `on_ready` event
- Modify embed colors and messages in the command functions
- Adjust conversation history length in `chat.py`

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

3. **Chat features not working:**
   - Check that your OpenRouter API key is correct in the `.env` file
   - Ensure you have credits in your OpenRouter account
   - Verify the API key has the necessary permissions

4. **Image generation fails:**
   - Check your internet connection
   - The Pollinations.ai API might be temporarily unavailable
   - Try with a different prompt

5. **Logging not working:**
   - Verify the log channel ID is correct
   - Make sure the bot has permission to send messages in the log channel
   - Check that the channel exists and is accessible

### Debug Mode

To enable debug logging, you can modify the bot to include more detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 API Information

### Image Generation
- **Service:** [Pollinations.ai](https://pollinations.ai/)
- **Endpoint:** `https://image.pollinations.ai/prompt/{prompt}`
- **Method:** GET request
- **Rate Limits:** Please be respectful with API usage
- **Image Format:** PNG/JPEG (automatically determined)

### Chat AI
- **Service:** [OpenRouter](https://openrouter.ai/)
- **Model:** `google/gemma-3n-e4b-it:free`
- **Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
- **Features:** Context-aware conversations, free tier available
- **Rate Limits:** Depends on your OpenRouter plan

## 🏗️ Architecture

### File Structure
```
hinata-discord-bot/
├── bot.py              # Main bot file and event handlers
├── commands.py         # Image generation commands
├── chat.py            # Chat functionality and channel management
├── logger.py          # Discord logging system
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
├── run.sh            # Startup script
├── test_api.py       # API testing script
└── README.md         # This file
```

### Key Components
- **HinataBot Class:** Main bot instance with event handling
- **ChatManager:** Manages channel activation and conversation history
- **DiscordLogger:** Comprehensive logging system for all bot activities
- **ImageCommands Cog:** Handles image generation commands
- **ChatCommands Cog:** Handles chat activation and management

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
3. Verify your Discord bot token and OpenRouter API key
4. Check the console output for error messages
5. Ensure the log channel ID is correct and accessible

## 🔄 Updates & Changelog

### Version 2.0 Features
- ✅ AI Chat functionality with Google Gemma model
- ✅ Channel activation system for automatic responses
- ✅ Comprehensive Discord logging system
- ✅ Smart detection between image and chat requests
- ✅ Context-aware conversations with history
- ✅ Enhanced error handling and user feedback

### Version 1.0 Features
- ✅ Image generation with Pollinations.ai
- ✅ Multiple command types (slash, prefix, mention)
- ✅ Rich Discord embeds
- ✅ Basic error handling

---

**Made with ❤️ for the Discord community**

*Hinata combines the power of AI image generation and intelligent conversation to create the ultimate Discord assistant experience!*

