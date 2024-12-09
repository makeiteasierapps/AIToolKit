import asyncio
import logging
import os
from typing import Callable, Any
from dotenv import load_dotenv
from litellm.exceptions import InternalServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dspy import LM, configure

# Configure logging
logger = logging.getLogger('app.llm_utils')

# Load environment variables and configure models
load_dotenv()

MODEL_DICT = {
    'sonnet': {'model': 'anthropic/claude-3-5-sonnet-latest', 'max_tokens': 8192},
    'haiku': {'model': 'anthropic/claude-3-haiku-20240307', 'max_tokens': 4096},
    'opus': {'model': 'anthropic/claude-3-opus-latest', 'max_tokens': 4096},
    '4o-mini': {'model': 'openai/gpt-4o-mini', 'max_tokens': 4096},
    '4o': {'model': 'openai/gpt-4o', 'max_tokens': 4096},
}

# Initialize LLM configurations
def initialize_llm(lm='4o-mini', strong_lm='4o-mini'):
    # Verify API keys are present
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "REPLICATE_API_TOKEN"]
    for key in required_keys:
        if not os.environ.get(key):
            logger.warning(f"Missing {key} in environment variables")
    
    # Initialize LLM instances using the provided model names
    lm_instance = LM(MODEL_DICT[lm]['model'], max_tokens=MODEL_DICT[lm]['max_tokens'], cache=False)
    strong_lm_instance = LM(MODEL_DICT[strong_lm]['model'], max_tokens=MODEL_DICT[strong_lm]['max_tokens'], cache=False)
    configure(lm=lm_instance)
    
    return strong_lm_instance

@retry(
    retry=retry_if_exception_type(InternalServerError),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    before_sleep=lambda retry_state: logger.info(f"Retrying due to overload... attempt {retry_state.attempt_number}")
)
async def execute_llm_call(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Execute an LLM call with retry logic for handling rate limits and server overload.
    """
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)
    except InternalServerError as e:
        logger.warning(f"LLM overload error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in LLM call: {str(e)}")
        raise