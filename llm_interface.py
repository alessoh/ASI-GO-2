"""
LLM Interface supporting multiple providers
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger("ASI-GO.LLM")

class LLMInterface:
    """Unified interface for different LLM providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.client = None
        self.model = None
        
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected LLM provider"""
        try:
            if self.provider == "openai":
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in .env file")
                self.client = openai.OpenAI(api_key=api_key)
                self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
                
            elif self.provider == "google":
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in .env file")
                genai.configure(api_key=api_key)
                self.model = os.getenv("GOOGLE_MODEL", "gemini-pro")
                self.client = genai.GenerativeModel(self.model)
                
            elif self.provider == "anthropic":
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in .env file")
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
            logger.info(f"Initialized {self.provider} with model {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            raise
    
    def query(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2000) -> str:
        """Send a query to the LLM and return the response"""
        try:
            if self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            elif self.provider == "google":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self.client.generate_content(full_prompt)
                return response.text
                
            elif self.provider == "anthropic":
                messages = []
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            raise
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current provider"""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": str(self.temperature)
        }
        