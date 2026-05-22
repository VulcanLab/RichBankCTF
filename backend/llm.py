import os
from dotenv import load_dotenv

load_dotenv()

def get_llm(tools=None):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        kwargs = {
            "api_key":  os.getenv("OPENAI_API_KEY"),
            "model":    os.getenv("OPENAI_MODEL", "gpt-4o"),
        }
        base_url = os.getenv("OPENAI_BASE_URL", "")
        if base_url:
            kwargs["base_url"] = base_url
        llm = ChatOpenAI(**kwargs)

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

    if tools:
        return llm.bind_tools(tools)
    return llm
