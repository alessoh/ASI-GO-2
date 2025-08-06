"""
Test OpenAI initialization
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing OpenAI initialization...")
print(f"Python OpenAI version: 1.12.0")

try:
    from openai import OpenAI
    print("✓ OpenAI import successful")
    
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"✓ API Key found: {'Yes' if api_key else 'No'}")
    
    if api_key:
        # Try to initialize the client
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized successfully")
        
        # Try a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello, ASI-GO!'"}],
            max_tokens=50
        )
        print(f"✓ API call successful: {response.choices[0].message.content}")
    else:
        print("✗ No API key found in .env file")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()