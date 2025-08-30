import os
from typing import Optional


def get_litellm_model() -> str:
	# Use Groq model by default, but allow override
	model = os.getenv("LITELLM_MODEL", "groq/llama3-70b-8192")
	# Ensure Groq prefix for Groq API keys
	if os.getenv("GROQ_API_KEY") and not model.startswith("groq/"):
		model = f"groq/{model}"
	return model


def get_litellm_api_key() -> Optional[str]:
	# Support multiple API key formats for different providers
	return os.getenv("LITELLM_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")


def get_proxy() -> Optional[str]:
	return os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
