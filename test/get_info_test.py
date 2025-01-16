# -*- coding: utf-8 -*-
import os, re, sys
import json
import asyncio
import time
from prompts import *
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # get parent dir
sys.path.append(project_root)

from core.llms.openai_wrapper import openai_llm as llm

benchmark_model = 'Qwen/Qwen2.5-72B-Instruct'
models = ['Qwen/Qwen2.5-7B-Instruct', 'Qwen/Qwen2.5-14B-Instruct',  'Qwen/Qwen2.5-32B-Instruct', 'deepseek-ai/DeepSeek-V2.5', 'internlm/internlm2_5-20b-chat']
async def main(texts: list[str], link_dict: dict, record_file: str, sys_prompt: str, focus_points: list):
    # first get more links
    print(f'sys_prompt: \n{sys_prompt}')
    benchmark_result = None
    for model in [benchmark_model] + models:
        _texts = []
        for text in texts:
            _texts.extend(text.split('\n\n'))
        print(f"running {model} ...")
        start_time = time.time()
        hallucination_times = 0
        text_batch = ''
        cache = set()
        while _texts:
            t = _texts.pop(0)
            text_batch = f'{text_batch}{t}\n\n'
            if len(text_batch) > 512 or len(_texts) == 0:
                content = f'<text>\n{text_batch}</text>\n\n{get_info_suffix}'
                result = await llm(
                    [{'role': 'system', 'content': sys_prompt}, {'role': 'user', 'content': content}],
                    model=model, temperature=0.1)
                print(f"llm output\n{result}\n")
                result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
                if result:
                    # 在result[-1]中找到所有类似[4]这样的片段
                    links = re.findall(r'\[\d+\]', result[-1])
                    for link in links:
                        if link not in text_batch:
                            hallucination_times += 1
                            print(f'\n**not in text_batch: {link}**\n')
                            continue
                        cache.add(link)
                text_batch = ''

        t1 = time.time()
        get_infos_time = t1 - start_time
        print(f"get more infos time: {get_infos_time}")
        print("*" * 12)
        print('\n\n')

        for link in cache:
            if link not in link_dict:
                print(f'\n**not in link_dict: {link}**\n')
        if model == benchmark_model:
            benchmark_result = cache.copy()
            diff = 'benchmark'
        else:
            # 计算当前cache与benchmark的差异
            missing_in_cache = len(benchmark_result - cache)  # benchmark中有但cache中没有的
            extra_in_cache = len(cache - benchmark_result)    # cache中有但benchmark中没有的
            total_diff = missing_in_cache + extra_in_cache
            diff = f'差异{total_diff}个(遗漏{missing_in_cache}个,多出{extra_in_cache}个)'

        infos_to_record = '\n'.join(list(set(link_dict[link] for link in cache)))

        with open(record_file, 'a') as f:
            f.write(f"llm model: {model}\n")
            f.write(f"process time: {get_infos_time} s\n")
            f.write(f"bad generate times: {hallucination_times}\n")
            f.write(f"diff from benchmark: {diff}\n")
            f.write(f"segments: \n{infos_to_record}\n")
            f.write("*" * 12)
            f.write('\n\n')
 

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_dir', '-D', type=str, default='')
    args = parser.parse_args()

    sample_dir = args.sample_dir

    if not os.path.exists(os.path.join(sample_dir, 'focus_point.json')):
        raise ValueError(f'{sample_dir} focus_point.json not found')
    
    focus_points = json.load(open(os.path.join(sample_dir, 'focus_point.json'), 'r'))
    focus_statement = ''
    for item in focus_points:
        tag = item["focuspoint"]
        expl = item["explanation"]
        focus_statement = f"{focus_statement}//{tag}//\n"
        if expl:
            focus_statement = f"{focus_statement}解释：{expl}\n"

    get_info_system = get_info_system.replace('{focus_statement}', focus_statement)
    system_prompt = f"今天的日期是{datetime.now().strftime('%Y-%m-%d')}，{get_info_system}"
    focus_points = [item["focuspoint"] for item in focus_points]

    time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    record_file = os.path.join(sample_dir, f'record-{time_stamp}.txt')
    with open(record_file, 'w') as f:
        f.write(f"focus statement: \n{focus_statement}\n\n")

    for dirs in os.listdir(sample_dir):
        if not os.path.isdir(os.path.join(sample_dir, dirs)):
            continue
        _path = os.path.join(sample_dir, dirs)
        print(f'start testing {_path}')
        if 'sample.json' not in os.listdir(_path):
            print(f'{dirs} sample.json not found, skip')
            continue
        sample = json.load(open(os.path.join(_path, 'sample.json'), 'r'))

        with open(record_file, 'a') as f:
            f.write(f"raw materials in: {dirs}\n\n")
        asyncio.run(main(sample['links_part'], sample['link_dict'], record_file, system_prompt, focus_points))
