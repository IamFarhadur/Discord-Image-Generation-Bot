#!/usr/bin/env python3
"""
Test script for OpenRouter API integration
This script tests the chat functionality without requiring Discord setup
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

def test_openrouter_connection():
    """Test OpenRouter API connection and chat functionality"""
    print("🌸 Hinata Bot - OpenRouter API Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables!")
        print("Please add your OpenRouter API key to the .env file.")
        return False
    
    if api_key == "your_openrouter_api_key_here":
        print("❌ Error: Please replace the placeholder API key with your actual OpenRouter API key!")
        return False
    
    print(f"🔑 API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Initialize OpenRouter client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        print("🔗 Testing connection to OpenRouter...")
        
        # Test message
        test_messages = [
            {
                "role": "system",
                "content": "You are Hinata, a friendly and helpful Discord bot. Respond briefly and cheerfully."
            },
            {
                "role": "user",
                "content": "Hello! Can you introduce yourself?"
            }
        ]
        
        # Make API call
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://discord.com",
                "X-Title": "Hinata Discord Bot Test",
            },
            model="google/gemma-3n-e4b-it:free",
            messages=test_messages,
            max_tokens=200,
            temperature=0.7
        )
        
        response = completion.choices[0].message.content
        
        print("✅ Connection successful!")
        print(f"🤖 Model: google/gemma-3n-e4b-it:free")
        print(f"💬 Test Response:")
        print(f"   {response}")
        print()
        
        # Test conversation flow
        print("🔄 Testing conversation flow...")
        
        conversation = [
            {
                "role": "system",
                "content": "You are Hinata, a friendly Discord bot. Keep responses short and cheerful."
            },
            {
                "role": "user",
                "content": "TestUser: What can you help me with?"
            }
        ]
        
        completion2 = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://discord.com",
                "X-Title": "Hinata Discord Bot Test",
            },
            model="google/gemma-3n-e4b-it:free",
            messages=conversation,
            max_tokens=150,
            temperature=0.7
        )
        
        response2 = completion2.choices[0].message.content
        
        print(f"💬 Conversation Response:")
        print(f"   {response2}")
        print()
        
        print("🎉 All tests passed! OpenRouter integration is working correctly.")
        print("💡 Your Hinata bot should be able to chat successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenRouter API: {e}")
        print()
        print("🔍 Troubleshooting tips:")
        print("1. Check that your OpenRouter API key is correct")
        print("2. Ensure you have credits in your OpenRouter account")
        print("3. Verify your internet connection")
        print("4. Check if the OpenRouter service is available")
        
        return False

def main():
    """Run OpenRouter API tests"""
    success = test_openrouter_connection()
    
    if success:
        print("\n" + "=" * 40)
        print("🚀 Ready to run Hinata with chat features!")
        print("Run 'python bot.py' to start the bot.")
    else:
        print("\n" + "=" * 40)
        print("⚠️  Chat features may not work properly.")
        print("Image generation will still work without OpenRouter.")

if __name__ == "__main__":
    main()

