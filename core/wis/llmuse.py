import os
from openai import OpenAI
from openai import RateLimitError, APIError
import time
from async_logger import wis_logger
from typing import List

base_url = os.environ.get('LLM_API_BASE', "")
token = os.environ.get('LLM_API_KEY', "")
primary_model = os.environ.get("PRIMARY_MODEL", "")

if not base_url and not token:
    raise ValueError("LLM_API_BASE or LLM_API_KEY must be set")
elif base_url and not token:
    client = OpenAI(base_url=base_url, api_key="not_use")
elif not base_url and token:
    client = OpenAI(api_key=token)
else:
    client = OpenAI(api_key=token, base_url=base_url)

def perform_completion_with_backoff(messages: List, model: str = '', **kwargs):
    model = model if model else primary_model
    max_retries = 3
    wait_time = 20
    for retry in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=model,
                **kwargs
            )
            return response
        except RateLimitError as e:
            # rate limit error, retry
            error_msg = f"{model} Rate limit error: {str(e)}. Retry {retry+1}/{max_retries}."
            wis_logger.warning(error_msg)
        except APIError as e:
            if hasattr(e, 'status_code'):
                if e.status_code in [400, 401, 413]:
                    # client error, no need to retry
                    error_msg = f"{model} API error: {e.status_code}. Detail: {str(e)}"
                    if (
                        'Image url should be a valid url or should like data:image/TYPE;base64' not in error_msg and
                        'Failed to process image URL: data:' not in error_msg
                        ):
                        # image url probility is that server cannot fetch the image, so we don't need to worry about it
                        wis_logger.warning(error_msg)
                        wis_logger.info(f"messages: {messages}")
                    raise e
                else:
                    # other API error, retry
                    error_msg = f"{model} API error: {e.status_code}. Retry {retry+1}/{max_retries}."
                    wis_logger.warning(error_msg)
            else:
                # unknown API error, retry
                error_msg = f"{model} Unknown API error: {str(e)}. Retry {retry+1}/{max_retries}."
                wis_logger.warning(error_msg)
        except Exception as e:
            # other exception, retry
            error_msg = f"{model} Unexpected error: {str(e)}. Retry {retry+1}/{max_retries}."
            wis_logger.warning(error_msg)

        if retry < max_retries - 1:
            # exponential backoff strategy
            time.sleep(wait_time)
            # next wait time is doubled
            wait_time *= 2

    # if all retries fail
    error_msg = "Max retries reached, still unable to get a valid response."
    wis_logger.warning(error_msg)
    raise Exception(error_msg)
