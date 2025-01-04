# -*- coding: utf-8 -*-
import os, re, sys
import json
import asyncio
import time
from prompts import *

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # get parent dir
sys.path.append(project_root)

from core.llms.openai_wrapper import openai_llm as llm

models = ['Qwen/Qwen2.5-14B-Instruct',  'Qwen/Qwen2.5-32B-Instruct', 'deepseek-ai/DeepSeek-V2.5', 'Qwen/Qwen2.5-72B-Instruct']

async def main(link_dict: dict, text: str, record_file: str, prompts: list, focus_points: list):
    # first get more links
    _to_be_processed = []
    link_map = {}
    for i, (url, des) in enumerate(link_dict.items()):
        des = des.replace('\n', ' ')
        _to_be_processed.append(f'<t{i+1}>//{des}//')
        link_map[f'<t{i+1}'] = url

    for model in models:
        print(f"running {model} ...")
        start_time = time.time()
        get_more_links_hallucination_times = 0
        more_links = set()
        text_batch = ''
        for t in _to_be_processed:
            text_batch = f'{text_batch}{t}\n'
            if len(text_batch) > 2048:
                content = f'<text>\n{text_batch}</text>\n\n{text_link_suffix}'
                result = await llm(
                    [{'role': 'system', 'content': prompts[0]}, {'role': 'user', 'content': content}],
                    model=model, temperature=0.1)
                print(f"llm output\n{result}")
                text_batch = ''
                result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
                result = result[-1]
                for item in result.split('\n'):
                    if not item:
                        continue
                    segs = item.split('>')
                    if len(segs) != 2:
                        get_more_links_hallucination_times += 1
                        continue
                    _index, focus = segs
                    _index = _index.strip()
                    focus = focus.strip().strip('//')
                    if focus == 'NA':
                        continue
                    if focus not in focus_points or _index not in link_map:
                        get_more_links_hallucination_times += 1
                        continue
                    more_links.add(link_map[_index])
                
        if text_batch:
            content = f'<text>\n{text_batch}</text>\n\n{text_link_suffix}'
            result = await llm(
                [{'role': 'system', 'content': prompts[0]}, {'role': 'user', 'content': content}],
                model=model, temperature=0.1)
            print(f"llm output\n{result}")
            result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
            result = result[-1]
            for item in result.split('\n'):
                if not item:
                    continue
                segs = item.split('>')
                if len(segs) != 2:
                    get_more_links_hallucination_times += 1
                    continue
                _index, focus = segs
                _index = _index.strip()
                focus = focus.strip().strip('//')
                if focus == 'NA':
                    continue
                if focus not in focus_points or _index not in link_map:
                    get_more_links_hallucination_times += 1
                    continue
                more_links.add(link_map[_index])

        t1 = time.time()
        get_more_links_time = t1 - start_time
        print(f"get more links time: {get_more_links_time}")

        # second get more infos
        lines = text.split('\n')
        cache = set()
        text_batch = ''
        for line in lines:
            text_batch = f'{text_batch}{line}\n'
            if len(text_batch) > 5000:
                #print(f"text_batch\n{text_batch}")
                content = f'<text>\n{text_batch}</text>\n\n{text_info_suffix}'
                result = await llm(
                    [{'role': 'system', 'content': prompts[1]}, {'role': 'user', 'content': content}],
                    model=model, temperature=0.1)
                print(f"llm output\n{result}")
                text_batch = ''
                result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
                cache.add(result[-1])

        if text_batch:
            #print(f"text_batch\n{text_batch}")
            content = f'<text>\n{text_batch}</text>\n\n{text_info_suffix}'
            result = await llm(
                [{'role': 'system', 'content': prompts[1]}, {'role': 'user', 'content': content}],
                model=model, temperature=0.1)
            print(f"llm output\n{result}")
            result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
            cache.add(result[-1])

        get_infos_hallucination_times = 0
        infos = []
        for item in cache:
            segs = item.split('//')
            i = 0
            while i < len(segs) - 1:
                focus = segs[i].strip()
                if not focus:
                    i += 1
                    continue
                if focus not in focus_points:
                    get_infos_hallucination_times += 1
                    i += 1
                    continue
                content = segs[i+1].strip().strip('摘要').strip(':').strip('：')
                i += 2
                if content and content != 'NA':
                    infos.append(f'{focus}: {content}')
            """
            maybe can use embedding retrieval to judge
            """
        t2 = time.time()
        get_infos_time = t2 - t1
        print(f"get more infos time: {get_infos_time}")

        # get author and publish date from text
        if len(text) > 1024:
            usetext = f'{text[:500]}......{text[-500:]}'
        else:
            usetext = text
        content = f'<text>\n{usetext}\n</text>\n\n{text_ap_suffix}'
        llm_output = await llm([{'role': 'system', 'content': text_ap_system}, {'role': 'user', 'content': content}],
                               model=model, max_tokens=50, temperature=0.1)
        print(f"llm output: {llm_output}")
        ap_ = llm_output.strip().strip('"')

        print("*" * 12)
        print('\n\n')

        more_links_to_record = [f'{link_dict[link]}:{link}' for link in more_links]
        more_links_to_record = '\n'.join(more_links_to_record)
        infos_to_record = '\n'.join(infos)

        with open(record_file, 'a') as f:
            f.write(f"llm model: {model}\n")
            f.write(f"get more links time: {get_more_links_time} s\n")
            f.write(f"bad generate times during get more links: {get_more_links_hallucination_times}\n")
            f.write(f"get more infos time: {get_infos_time} s\n")
            f.write(f"bad generate times during get more infos: {get_infos_hallucination_times}\n")
            f.write(f"total more links: {len(more_links)}\n")
            f.write(f"total infos: {len(infos)}\n")
            f.write(f"author and publish time: {ap_}\n")
            f.write(f"infos: \n{infos_to_record}\n")
            f.write(f"more links: \n{more_links_to_record}\n")
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

    get_info_system = text_info_system.replace('{focus_statement}', focus_statement)
    get_link_system = text_link_system.replace('{focus_statement}', focus_statement)
    prompts = [get_link_system, get_info_system]
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
        if 'sample_recognized.json' not in os.listdir(_path):
            print(f'{dirs} sample_recognized.json not found, use sample.json instead')
            if 'sample.json' not in os.listdir(_path):
                print(f'{dirs} sample.json not found, skip')
                continue
            sample_recognized = json.load(open(os.path.join(_path, 'sample.json'), 'r'))
        else:
            sample_recognized = json.load(open(os.path.join(_path, 'sample_recognized.json'), 'r'))
        
        link_dict = sample_recognized['link_dict']
        text = sample_recognized['text']
        with open(record_file, 'a') as f:
            f.write(f"raw materials in: {dirs}\n\n")
        asyncio.run(main(link_dict, text, record_file, prompts, focus_points))
