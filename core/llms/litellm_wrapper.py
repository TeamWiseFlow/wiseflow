from litellm import Router
from litellm.router import RetryPolicy, AllowedFailsPolicy
from pydantic import BaseModel, Field
import os


retry_policy = RetryPolicy(
    ContentPolicyViolationErrorRetries=3,         # run 3 retries for ContentPolicyViolationErrors
    AuthenticationErrorRetries=0,                 # run 0 retries for AuthenticationErrorRetries
    BadRequestErrorRetries=1,
    TimeoutErrorRetries=2,
    RateLimitErrorRetries=3,
)

allowed_fails_policy = AllowedFailsPolicy(
    ContentPolicyViolationErrorAllowedFails=100, # Allow 100 ContentPolicyViolationError before cooling down a deployment
    RateLimitErrorAllowedFails=10,               # Allow 10 RateLimitErrors before cooling down a deployment
)

class RouterGeneralSettings(BaseModel):
    async_only_mode: bool = True

providers = ['openai', 'deepseek', 'openrouter', 'baseten', 'jina_ai', 'voyage', 'together_ai', 'togethercomputer', 'ai21', 'deepinfra', 'cloudflare',
            'hosted_vllm', 'fireworks_ai', 'github', 'groq', 'perplexity', 'ollama', 'triton', 'volcengine', 'xai', 'nvidia_nim', 'huggingface',
            'mistral', 'bedrock', 'sagemaker', 'gemini', 'azure_ai']

base_url = os.environ.get('LLM_API_BASE', "")
api_key = os.environ.get('LLM_API_KEY', "")
model = os.environ.get("PRIMARY_MODEL", "")
if not model or not api_key:
    raise ValueError("PRIMARY_MODEL or LLM_API_KEY not set, please set it in environment variables or edit core/.env")
secondary_model = os.environ.get("SECONDARY_MODEL", model)

vl_model = os.environ.get("VL_MODEL", "")
if not vl_model:
    print("VL_MODEL not set, will skip extracting info from img, some info may be lost!")

model_provider = model.split('/')[0]
if model_provider not in providers:
    model_provider = 'openai'

secondary_model_provider = secondary_model.split('/')[0]
if secondary_model_provider not in providers:
    secondary_model_provider = 'openai'

vl_model_provider = vl_model.split('/')[0]
if vl_model_provider not in providers:
    vl_model_provider = 'openai'


router = Router(
    model_list=[
        {
            "model_name": 'Pro/Qwen/Qwen2-VL-7B-Instruct',
            "litellm_params": {
                "model": "openai/Pro/Qwen/Qwen2-VL-7B-Instruct",
                "api_key": api_key,
                "api_base": base_url,
            },
        },
        {
            "model_name": 'OpenGVLab/InternVL2-26B',
            "litellm_params": {
                "model": 'openai/OpenGVLab/InternVL2-26B',
                "api_key": api_key,
                "api_base": base_url,
            },
        },
        {
            "model_name": 'deepseek-ai/deepseek-vl2',
            "litellm_params": {
                # "model": f"{vl_model_provider}/{vl_model}",
                "model": 'openai/deepseek-ai/deepseek-vl2',
                "api_key": api_key,
                "api_base": base_url,
            },
        },
    ],
    retry_policy=retry_policy,
    allowed_fails_policy=allowed_fails_policy,
    default_max_parallel_requests=int(os.environ.get('LLM_CONCURRENT_NUMBER', 1)), 
    cooldown_time=30,
    router_general_settings=RouterGeneralSettings(async_only_mode=True),
    set_verbose=True,
    debug_level="DEBUG" 
)


async def litellm_llm(messages: list, model: str, logger=None, **kwargs) -> str:
    try:
        response = await router.acompletion(model=model, messages=messages, **kwargs)
        resp = response.choices[0].message.content
        print(f'usage:\n {response.usage}')
        if logger:
            logger.debug(f'usage:\n {response.usage}')
    except Exception as e:
        if logger:
            logger.error(e)
        else:
            print(e)
    return resp
