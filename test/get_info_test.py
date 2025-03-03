# -*- coding: utf-8 -*-
import os, sys
import json
import asyncio
import time
from datetime import datetime

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

from dotenv import load_dotenv
env_path = os.path.join(core_path, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from utils.general_utils import is_chinese
from agents.get_info import get_author_and_publish_date, get_info, get_more_related_urls
from agents.get_info_prompts import *


benchmark_model = 'Qwen/Qwen2.5-72B-Instruct'
# benchmark_model = 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B'
# models = ['deepseek-ai/DeepSeek-R1-Distill-Qwen-7B', 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B', 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B']
models = ['Qwen/Qwen2.5-7B-Instruct', 'Qwen/Qwen2.5-14B-Instruct',  'Qwen/Qwen2.5-32B-Instruct', 'deepseek-ai/DeepSeek-V2.5']

async def main(sample: dict, include_ap: bool, prompts: list, record_file: str):
    link_dict, links_parts, contents = sample['link_dict'], sample['links_part'], sample['contents']
    get_link_sys_prompt, get_link_suffix_prompt, get_info_sys_prompt, get_info_suffix_prompt = prompts

    for model in [benchmark_model] + models:
        links_texts = []
        for _parts in links_parts:
            links_texts.extend(_parts.split('\n\n'))
        contents = sample['contents'].copy()

        print(f"running {model} ...")
        start_time = time.time()
        if include_ap:
            author, publish_date = await get_author_and_publish_date('# '.join(contents), model, test_mode=True)
            get_ap_time = time.time() - start_time
            print(f"get author and publish date time: {get_ap_time}")
        else:
            author, publish_date = '', ''
            get_ap_time = 0

        start_time = time.time()
        more_url = await get_more_related_urls(links_texts, link_dict, [get_link_sys_prompt, get_link_suffix_prompt, model], test_mode=True)
        get_more_url_time = time.time() - start_time
        print(f"get more related urls time: {get_more_url_time}")

        start_time = time.time()
        infos = await get_info(contents, link_dict, [get_info_sys_prompt, get_info_suffix_prompt, model], author, publish_date, test_mode=True)
        get_info_time = time.time() - start_time
        print(f"get info time: {get_info_time}")

        if model == benchmark_model:
            benchmark_result = more_url.copy()
            diff = f'benchmark: {len(benchmark_result)} results'
        else:
            missing_in_cache = len(benchmark_result - more_url)  # benchmark中有但cache中没有的
            extra_in_cache = len(more_url - benchmark_result)    # cache中有但benchmark中没有的
            total_diff = missing_in_cache + extra_in_cache
            diff = f'差异{total_diff}个(遗漏{missing_in_cache}个,多出{extra_in_cache}个)'

        related_urls_to_record = '\n'.join(more_url)
        infos_to_record = [fi['content'] for fi in infos]
        infos_to_record = '\n'.join(infos_to_record)
        with open(record_file, 'a') as f:
            f.write(f"model: {model}\n")
            if include_ap:
                f.write(f"get author and publish date time: {get_ap_time}\n")
                f.write(f"author: {author}\n")
                f.write(f"publish date: {publish_date}\n")
            f.write(f"get more related urls time: {get_more_url_time}\n")
            f.write(f"diff from benchmark: {diff}\n")
            f.write(f"get info time: {get_info_time}\n")
            f.write(f"related urls: \n{related_urls_to_record}\n")
            f.write(f"final result: \n{infos_to_record}\n")
            f.write('\n\n')
        print('\n\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_dir', '-D', type=str, default='')
    parser.add_argument('--include_ap', '-I', type=bool, default=False)
    args = parser.parse_args()

    sample_dir = args.sample_dir
    include_ap = args.include_ap
    if not os.path.exists(os.path.join(sample_dir, 'focus_point.json')):
        raise ValueError(f'{sample_dir} focus_point.json not found')
    
    focus_points = json.load(open(os.path.join(sample_dir, 'focus_point.json'), 'r'))
    focus_statement = ''
    for item in focus_points:
        tag = item["focuspoint"].strip()
        expl = item["explanation"].strip()
        focus_statement = f"{focus_statement}//{tag}//"
        if expl:
            if is_chinese(expl):
                focus_statement = f"{focus_statement}\n解释：{expl}\n"
            else:
                focus_statement = f"{focus_statement}\nExplanation: {expl}\n"
    
    #focus_dict = {item["focuspoint"]: item["focuspoint"] for item in focus_points}
    date_stamp = datetime.now().strftime('%Y-%m-%d')
    if is_chinese(focus_statement):
        get_link_sys_prompt = get_link_system.replace('{focus_statement}', focus_statement)
        get_link_sys_prompt = f"今天的日期是{date_stamp}，{get_link_sys_prompt}"
        get_link_suffix_prompt = get_link_suffix
        get_info_sys_prompt = get_info_system.replace('{focus_statement}', focus_statement)
        get_info_sys_prompt = f"今天的日期是{date_stamp}，{get_info_sys_prompt}"
        get_info_suffix_prompt = get_info_suffix
    else:
        get_link_sys_prompt = get_link_system_en.replace('{focus_statement}', focus_statement)
        get_link_sys_prompt = f"today is {date_stamp}, {get_link_sys_prompt}"
        get_link_suffix_prompt = get_link_suffix_en
        get_info_sys_prompt = get_info_system_en.replace('{focus_statement}', focus_statement)
        get_info_sys_prompt = f"today is {date_stamp}, {get_info_sys_prompt}"
        get_info_suffix_prompt = get_info_suffix_en

    prompts = [get_link_sys_prompt, get_link_suffix_prompt, get_info_sys_prompt, get_info_suffix_prompt]

    time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    record_file = os.path.join(sample_dir, f'record-{time_stamp}.txt')
    with open(record_file, 'w') as f:
        f.write(f"focus statement: \n{focus_statement}\n\n")

    for file in os.listdir(sample_dir):
        if not file.endswith('_processed.json'):
            continue
        sample = json.load(open(os.path.join(sample_dir, file), 'r'))
        if 'links_part' not in sample or 'link_dict' not in sample or 'contents' not in sample:
            print(f'{file} not valid sample, skip')
            continue
        with open(record_file, 'a') as f:
            f.write(f"raw materials: {file}\n\n")
        print(f'start testing {file}')
        asyncio.run(main(sample, include_ap, prompts, record_file))
