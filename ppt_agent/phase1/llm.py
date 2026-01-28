from pathlib import Path
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from phase1.config import load_yaml_config
from phase1.config.agents import LLMType

# Cache for LLM instances
_llm_cache = {}

def _create_llm_use_conf(llm_type: LLMType, conf: Dict[str, Any]) -> ChatGoogleGenerativeAI:
    
    llm_type_map = {
        "reasoning": conf.get("REASONING_MODEL"),
        "basic": conf.get("BASIC_MODEL"),
        "vision": conf.get("VISION_MODEL"),
    }
    llm_conf = llm_type_map.get(llm_type)
    if not llm_conf:
        raise ValueError(f"Unknown LLM type: {llm_type}")
    if not isinstance(llm_conf, dict):
        raise ValueError(f"Invalid LLM Conf: {llm_type}")
    
    # Convert OpenAI-style params to Gemini params if needed
    gemini_conf = {}
    if "model" in llm_conf:
        gemini_conf["model"] = llm_conf["model"]
    if "temperature" in llm_conf:
        gemini_conf["temperature"] = llm_conf["temperature"]
    # IMPORTANT: Pass the API key!
    if "google_api_key" in llm_conf:
        gemini_conf["google_api_key"] = llm_conf["google_api_key"]
    
    return ChatGoogleGenerativeAI(**gemini_conf)

def get_llm_by_type(llm_type: LLMType) -> ChatGoogleGenerativeAI:
    
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]
    print(str((Path(__file__).parent.parent.parent / "conf.yaml").resolve()))
    conf = load_yaml_config(
        str("Documents\cursor\\agents_learning\ppt_agent\phase1\conf.yaml")
    )
    print(conf)
    llm = _create_llm_use_conf(llm_type, conf)
    print(llm)
    _llm_cache[llm_type] = llm
    return llm

# Pre-initialize common LLMs
try:
    basic_llm = get_llm_by_type("basic")
except Exception as e:
    print(f"Warning: Failed to initialize basic LLM: {e}")