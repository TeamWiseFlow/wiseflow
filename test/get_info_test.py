# -*- coding: utf-8 -*-

import os, re
import json
import asyncio
import time
from prompts import *
import json_repair
from openai_wrapper import openai_llm as llm
from find_article_or_list import find_article_or_list, common_tlds, common_file_exts

sample_dir = 'webpage_samples'
models = ['deepseek-ai/DeepSeek-V2.5', 'Qwen/Qwen2.5-Coder-32B-Instruct', 'Qwen/Qwen2.5-32B-Instruct', 'Qwen/Qwen2.5-14B-Instruct', 'Qwen/Qwen2.5-Coder-7B-Instruct']
secondary_mpdel = 'Qwen/Qwen2.5-7B-Instruct'
vl_model = ''

async def generate_results(text, model, system_prompt, suffix_prompt) -> set:
    lines = text.split('\n')
    cache = set()
    text_batch = ''
    for line in lines:
        text_batch = f'{text_batch}\n{line}'
        if len(text_batch) > 1024:
            content = f'<text>\n{text_batch}\n</text>\n\n{suffix_prompt}'
            result = await llm(
                [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': content}],
                model=model, temperature=0.1)
            print(f"llm output: {result}")
            result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
            if not result:
                print(f"warning: bad generate result")
                text_batch = ''
                continue
            result = result[0].strip()
            result = result.split('\n')
            cache.update(result)
            text_batch = ''

    if text_batch:
        content = f'<text>\n{text_batch}\n</text>\n\n{suffix_prompt}'
        result = await llm(
            [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': content}],
            model=model, temperature=0.1)
        print(f"llm output: {result}")
        result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
        if not result:
            print(f"warning: bad generate result")
            return cache
        result = result[0].strip()
        result = result.split('\n')
        cache.update(result)
    return cache


async def extract_info_from_img(text, link_dict) -> str:
    cache = {}
    pattern = r'<img>\[url\d+\]'
    matches = re.findall(pattern, text)
    for match in matches:
        key = match.split('[url')[1][:-1]
        url = link_dict.get(f'url{key}', '')
        if not url:
            continue
        
        if url in cache:
            replace_text = cache[url]
        else:
            if any(url.lower().endswith(tld) for tld in common_tlds):
                continue
            if any(url.lower().endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
                continue
            llm_output = await llm([{"role": "user",
                                "content": [{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
                                             {"type": "text", "text": image_system}]}], model='OpenGVLab/InternVL2-26B')
            print(f"vl model output: \n{llm_output}\n")
            replace_text = llm_output
            cache[url] = replace_text
        text = text.replace(match, f'{replace_text}{match}', 1)
    return text


async def main(link_dict, text, record_file, prompts):
    is_list, need_more_info, text = find_article_or_list(link_dict, text)

    if is_list:
        print("may be a article list page, get more urls ...")
        system_prompt = prompts[1]
        suffix_prompt = text_link_suffix
    else:
        if need_more_info:
            print("may be a article page need to get more text from images...")
            text = await extract_info_from_img(text, link_dict)
            print(f"extended text: \n{text}\n")

        system_prompt = prompts[0]
        suffix_prompt = text_info_suffix

    for model in models:
        print(f"running {model} ...")
        start_time = time.time()
        hallucination_times = 0
        
        raw_result = await generate_results(text, model, system_prompt, suffix_prompt)
        final_result = set()
        for item in raw_result:
            if is_list:
                if '[url' not in item:
                    hallucination_times += 1
                    continue
                # 从item中提取[]中的url标记
                url_tag = re.search(r'\[(.*?)]', item).group(1)
                if url_tag not in link_dict:
                    hallucination_times += 1
                    continue
                result_url = link_dict[url_tag]
                if any(result_url.lower().endswith(tld) for tld in common_tlds):
                    continue
                if any(result_url.lower().endswith(ext) for ext in common_file_exts):
                    continue
                final_result.add(item)
            else:
                result = json_repair.repair_json(item, return_objects=True)
                if not isinstance(result, dict):
                    hallucination_times += 1
                    continue
                if not result:
                    hallucination_times += 1
                    continue
                if 'focus' not in result or 'content' not in result:
                    hallucination_times += 1
                    continue
                if not result['content'].strip() or not result['focus'].strip():
                    hallucination_times += 1
                    continue
                if result['focus'].startswith('#'):
                    result['focus'] = result['focus'][1:]
                final_result.add(result)

        final_infos = '\n'.join(final_result)

        # get author and publish date from text
        if len(text) > 1024:
            usetext = f'{text[:500]}......{text[-500:]}'
        else:
            usetext = text
        content = f'<text>\n{usetext}\n</text>\n\n{text_ap_suffix}'
        llm_output = await llm([{'role': 'system', 'content': text_ap_system}, {'role': 'user', 'content': content}],
                               model=model, max_tokens=50, temperature=0.1, response_format={"type": "json_object"})
        print(f"llm output: {llm_output}")
        if not llm_output:
            hallucination_times += 1
            ap_ = {}
        else:
            result = json_repair.repair_json(llm_output, return_objects=True)
            if not isinstance(result, dict):
                hallucination_times += 1
                ap_ = {}
            else:
                ap_ = result

        total_analysis_time = time.time() - start_time
        print(f"text analysis finished, total time used: {total_analysis_time}")
        print("*" * 12)
        print('\n\n')

        with open(record_file, 'a') as f:
            f.write(f"llm model: {model}\n")
            f.write(f"hallucination times: {hallucination_times}\n")
            f.write(f"total analysis time: {total_analysis_time}\n\n")
            f.write(f"author and publish time(not formated): {ap_}\n")
            f.write(f"infos(not formated): \n{final_infos}\n")
            #f.write(f"more urls: \n{more_url_text}\n\n")
            f.write("*" * 12)
            f.write('\n\n')
 

if __name__ == '__main__':
    dirs = os.listdir(sample_dir)
    for _dir in dirs:
        if not _dir.startswith('task0'):
            continue
        _path = os.path.join(sample_dir, _dir)
        if not os.path.isdir(_path):
            continue
        if not os.path.exists(os.path.join(_path, 'focus_point.json')):
            print(f'{_dir} focus_point.json not found, skip')
            continue
        focus_points = json.load(open(os.path.join(_path, 'focus_point.json'), 'r'))
        focus_statement = ''
        for item in focus_points:
            tag = item["focuspoint"]
            expl = item["explanation"]
            focus_statement = f"{focus_statement}#{tag}\n"
            if expl:
                focus_statement = f"{focus_statement}解释：{expl}\n"

        print(f'start testing {_dir}')
        get_info_system = text_info_system.replace('{focus_statement}', focus_statement)
        get_link_system = text_link_system.replace('{focus_statement}', focus_statement)
        prompts = [get_info_system, get_link_system]

        samples = os.listdir(_path)
        time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        record_file = os.path.join(_path, f'record-{time_stamp}.txt')
        with open(record_file, 'w') as f:
            f.write(f"focus statement: \n{focus_statement}\n\n")
        for sample in samples:
            if not os.path.isdir(os.path.join(_path, sample)):
                continue
            files = os.listdir(os.path.join(_path, sample))
            if 'link_dict.json' not in files or 'text.txt' not in files:
                print(f'{sample} files not complete, skip')
                continue
            link_dict = json.load(open(os.path.join(_path, sample, 'link_dict.json'), 'r'))
            text = open(os.path.join(_path, sample, 'text.txt'), 'r').read()
            with open(record_file, 'a') as f:
                f.write(f"raw materials: {sample}\n\n")
            asyncio.run(main(link_dict, text, record_file, prompts))
