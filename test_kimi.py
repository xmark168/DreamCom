"""Test script để kiểm tra Kimi API."""

import asyncio
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from core.llm.factory import LLMClientFactory
from core.llm.base import LLMMessage


async def main():
    """Test Kimi API."""
    print("=" * 60)
    print("Testing Kimi API Connection")
    print("=" * 60)
    print()
    
    # Kiểm tra environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    default_model = os.getenv("DEFAULT_MODEL", "kimi-k2.5")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "Not set")
    print(f"Base URL: {base_url}")
    print(f"Default Model: {default_model}")
    print()
    
    try:
        # Tạo LLM client
        print("Creating LLM client...")
        llm_client = LLMClientFactory.create("openai", model=default_model)
        print(f"✅ Client created with model: {default_model}")
        print()
        
        # Test đơn giản
        print("Sending test message...")
        messages = [
            LLMMessage("system", "You are a helpful assistant."),
            LLMMessage("user", "Say 'Hello from Kimi!' and nothing else.")
        ]
        
        response = await llm_client.complete(messages, temperature=0.7)
        print(f"✅ Response received:")
        print(f"   Content: {response.content}")
        print(f"   Usage: {response.usage}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
