# Interface encapsulation for translation using Volcano Engine
# Set VOLC_KEY by environment variables in the format AK | SK
# AK-SK requires mobile phone number registration and real-name authentication, see here https://console.volcengine.com/iam/keymanage/(self-service access)
# Cost: Monthly free limit 2 million characters (1 Chinese character, 1 foreign language letter, 1 number, 1 symbol or space are counted as one character),
# exceeding 49 yuan/per million characters
# Picture translation: 100 pieces per month for free, 0.04 yuan/piece after exceeding
# Text translation concurrency limit, up to 16 per batch, the total text length does not exceed 5000 characters, max QPS is 10
# Terminology database management: https://console.volcengine.com/translate


import json
import time
import os
from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from volcengine.base.Service import Service


VOLC_KEY = os.environ.get('VOLC_KEY', None)
if not VOLC_KEY:
    raise Exception('Please set environment variables VOLC_KEY format as AK | SK')

k_access_key, k_secret_key = VOLC_KEY.split('|')


def text_translate(texts: list[str], target_language: str = 'zh', source_language: str = '', logger=None) -> list[str]:
    k_service_info = \
        ServiceInfo('translate.volcengineapi.com',
                    {'Content-Type': 'application/json'},
                    Credentials(k_access_key, k_secret_key, 'translate', 'cn-north-1'),
                    5,
                    5)
    k_query = {
        'Action': 'TranslateText',
        'Version': '2020-06-01'
    }
    k_api_info = {
        'translate': ApiInfo('POST', '/', k_query, {}, {})
    }
    service = Service(k_service_info, k_api_info)
    if source_language:
        body = {
            'TargetLanguage': target_language,
            'TextList': texts,
            'SourceLanguage': source_language
        }
    else:
        body = {
            'TargetLanguage': 'zh',
            'TextList': texts,
        }

    if logger:
        logger.debug(f'post body:\n {body}')

    for i in range(3):
        res = service.json('translate', {}, json.dumps(body))
        result = json.loads(res)

        if logger:
            logger.debug(f'result:\n {result}')

        if "Error" not in result["ResponseMetadata"]:
            break

        if result["ResponseMetadata"]["Error"]["Code"] in ['-400', '-415', '1000XX']:
            if logger:
                logger.warning(f"translation failed cause: {result['ResponseMetadata']['Error']['Message']}")
            else:
                print(f"translation failed cause: {result['ResponseMetadata']['Error']['Message']}")
            return []

        if logger:
            logger.warning(f"translation failed cause: {result['ResponseMetadata']['Error']['Message']}\n retry...")
        else:
            print(f"translation failed cause: {result['ResponseMetadata']['Error']['Message']}\n retry...")
        time.sleep(1)

    if "Error" in result["ResponseMetadata"]:
        if logger:
            logger.warning("translation service out of use, have retried 3 times...")
        else:
            print("translation service out of use, have retried 3 times...")

        return []

    return [_["Translation"] for _ in result["TranslationList"]]


if __name__ == '__main__':
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser(description='argparse')
    parser.add_argument("--file", "-F", type=str, default=None)
    parser.add_argument('--text', "-T", type=str, default="",
                        help="text to translate")
    parser.add_argument('--source', type=str, default="",
                        help="source language")
    parser.add_argument('--target', type=str, default='zh',
                        help="target language, default zh")

    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            raise FileNotFoundError("File {} not found".format(args.file))
        if not args.file.endswith(".txt"):
            raise ValueError("File {} should be a text file".format(args.file))
        with open(args.file, "r") as f:
            task = f.readlines()
        task = [_.strip() for _ in task if _.strip()]
    elif args.text:
        task = [args.text]
    else:
        raise ValueError("Please specify task or task file")

    start_time = time.time()
    pprint(text_translate(task, args.target, args.source))
    print("time cost: {}".format(time.time() - start_time))
