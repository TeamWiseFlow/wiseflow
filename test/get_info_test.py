# -*- coding: utf-8 -*-

import os, re
import json
import asyncio
import time, base64
from info_test_prompts import *
import json_repair
from llms.openai_wrapper import openai_llm as llm


sample_dir = 'test/webpage_samples'
models = ['deepseek-ai/DeepSeek-V2.5', 'Qwen/Qwen2.5-Coder-32B-Instruct', 'Qwen/Qwen2.5-32B-Instruct', 'Qwen/Qwen2.5-14B-Instruct', 'Qwen/Qwen2.5-Coder-7B-Instruct']
vl_models = ['Qwen/Qwen2-VL-72B-Instruct', 'OpenGVLab/InternVL2-26B', 'TeleAI/TeleMM', 'Pro/Qwen/Qwen2-VL-7B-Instruct', 'Pro/OpenGVLab/InternVL2-8B', 'OpenGVLab/InternVL2-Llama3-76B']

async def main(link_dict, text, screenshot_file, record_file, prompts):
    for model in models:
        print(f"running {model} ...")
        start_time = time.time()
        hallucination_times = 0
        # got more links from text
        # more_urls = set()
        more_url_text = set()
        content = ''
        for key in link_dict.keys():
            content = f"{content}{key}\n"
            if len(content) > 512:
                result = await llm([{'role': 'system', 'content': prompts[1]},
                                    {'role': 'user', 'content': f'<text>\n{content}\n</text>\n\n{text_link_suffix}'}],
                                   model=model, temperature=0.1)
                print(f"llm output: {result}")
                result = re.findall(r'"""(.*?)"""', result, re.DOTALL)
                if result:
                    result = result[0].strip()
                    result = result.split('\n')
                    # more_urls.update({link_dict[t] for t in result if t in link_dict})
                    more_url_text.update({f"{t}: {link_dict[t]}" for t in result if t in link_dict})
                else:
                    hallucination_times += len(result) - len({t for t in result if t in link_dict})
                content = ''

        if content:
            result = await llm([{'role': 'system', 'content': prompts[1]},
                                {'role': 'user', 'content': f'<text>\n{content}\n</text>\n\n{text_link_suffix}'}],
                               model=model, temperature=0.1)
            print(f"llm output: {result}")
            result = re.findall(r'"""(.*?)"""', result, re.DOTALL)
            if result:
                result = result[0].strip()
                result = result.split('\n')
                # more_urls.update({link_dict[t] for t in result if t in link_dict})
                more_url_text.update({f"{t}: {link_dict[t]}" for t in result if t in link_dict})
            else:
                hallucination_times += len(result) - len({t for t in result if t in link_dict})

        more_url_text = '\n'.join(more_url_text)
        print(f"time spent: {time.time() - start_time}")

        # get infos from text
        infos = []
        lines = text.split('\n')
        cache = ''
        for line in lines:
            cache = f'{cache}{line}'
            if len(cache) > 2048:
                content = f'<text>\n{cache}\n</text>\n\n{text_info_suffix}'
                result = await llm(
                    [{'role': 'system', 'content': prompts[0]}, {'role': 'user', 'content': content}],
                    model=model, temperature=0.1, response_format={"type": "json_object"})
                print(f"llm output: {result}")
                cache = ''
                if not result:
                    hallucination_times += 1
                    continue
                result = json_repair.repair_json(result, return_objects=True)
                if not isinstance(result, list):
                    hallucination_times += 1
                    continue
                if not result:
                    hallucination_times += 1
                    continue
                infos.extend(result)

        if cache:
            content = f'<text>\n{cache}\n</text>\n\n{text_info_suffix}'
            result = await llm([{'role': 'system', 'content': prompts[0]}, {'role': 'user', 'content': content}],
                               model=model, temperature=0.1, response_format={"type": "json_object"})
            print(f"llm output: {result}")
            if not result:
                hallucination_times += 1
            result = json_repair.repair_json(result, return_objects=True)
            if not isinstance(result, list):
                hallucination_times += 1
            if not result:
                hallucination_times += 1
            infos.extend(result)
        
        final_infos = []
        for item in infos:
            if 'focus' not in item or 'content' not in item:
                hallucination_times += 1
                continue
            if not item['content']:
                hallucination_times += 1
                continue
            if item['content'] in link_dict:
                continue

            final_infos.append(f"{item['focus']}: {item['content']}")

        final_infos = '\n'.join(final_infos)
        print(f"time spent: {time.time() - start_time}")

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
            f.write(f"more urls: \n{more_url_text}\n\n")
            f.write("*" * 12)
            f.write('\n\n')
 

if __name__ == '__main__':
    dirs = os.listdir(sample_dir)
    for _dir in dirs:
        if not _dir.startswith('task'):
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
        print(f"focus statement: {focus_statement}")
        get_info_system = text_info_system.replace('{focus_statement}', focus_statement)
        get_link_system = text_link_system.replace('{focus_statement}', focus_statement)
        #get_info_system = image_info_system.replace('{focus_statement}', focus_statement)
        #get_link_system = image_link_system.replace('{focus_statement}', focus_statement)
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
            if 'link_dict.json' not in files or 'text.txt' not in files or 'screenshot.jpg' not in files:
                print(f'{sample} files not complete, skip')
                continue
            link_dict = json.load(open(os.path.join(_path, sample, 'link_dict.json'), 'r'))
            text = open(os.path.join(_path, sample, 'text.txt'), 'r').read()
            screenshot_file = os.path.join(_path, sample, 'screenshot.jpg')
            with open(record_file, 'a') as f:
                f.write(f"raw materials: {sample}\n\n")
            asyncio.run(main(link_dict, text, screenshot_file, record_file, prompts))
"""
        with open(screenshot_file, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        print(f"run {model} testing...")
        start_time = time.time()
        hallucination_times = 0

        # get infos from image
        _infos = []
        llm_output = await llm([{"role": "system", "content": [{"type": "text", "text": image_info_system}]},
                                {"role": "user", "content": [{"type": "image_url",
                                                              "image_url": {
                                                                  "url": f"data:image/jpeg;base64,{base64_image}",
                                                                  "detail": "high"}},
                                                             {"type": "text", "text": image_info_suffix}]}],
                               model=model,
                               temperature=0.1)

        print(f"vl model output: \n{llm_output}")
        if not llm_output:
            hallucination_times += 1
            result = []
        else:
            result = json_repair.repair_json(llm_output, return_objects=True)
            if not isinstance(result, list):
                hallucination_times += 1
                result = []
            if not result:
                hallucination_times += 1
        _infos.extend(result)

        final_infos = []
        for item in _infos:
            if 'focus' not in item or 'content' not in item:
                hallucination_times += 1
                continue
            if not item['content']:
                hallucination_times += 1
                continue

            if item['content'] in link_dict:
                continue

            judge = await llm([{'role': 'system', 'content': verified_system},
                               {'role': 'user',
                                'content': f'<info>\n{item["content"]}\n</info>\n\n<text>\n{text}\n</text>\n\n{verified_suffix}'}],
                              model="THUDM/glm-4-9b-chat", temperature=0.1)
            if not judge:
                print('scondary model cannot judge')
                final_infos.append(item)
                continue

            to_save = False
            for i in range(min(7, len(judge))):
                char = judge[-1 - i]
                if char == '是':
                    to_save = True
                    break
                elif char == '否':
                    break
            if not to_save:
                hallucination_times += 1
                continue
            final_infos.append(item)

        print(f"final infos from image: {final_infos}")
        print(f"image hallucination times: {hallucination_times}")
        print(f"time used: {time.time() - start_time}")

        # get links from image
        more_links = set()
        llm_output = await llm([{"role": "system", "content": [{"type": "text", "text": image_link_system}]},
                                {"role": "user", "content": [{"type": "image_url",
                                                              "image_url": {
                                                                  "url": f"data:image/jpeg;base64,{base64_image}",
                                                                  "detail": "high"}},
                                                             {"type": "text", "text": image_link_suffix}]}],
                               model=model,
                               temperature=0.1)
        print(f"vl model output: \n{llm_output}")
        result = re.findall(r'\"\"\"(.*?)\"\"\"', llm_output, re.DOTALL)
        if result:
            result = result[0].strip()
        else:
            hallucination_times += 1
            result = []

        more_links = [link_dict[_t] for _t in result if _t in link_dict]
        print(f"more urls by image: {more_links}")
        print(f"image hallucination times: {hallucination_times}")
        print(f"time used: {time.time() - start_time}")

        # get author and publish date from image
        llm_output = await llm([{"role": "system", "content": [{"type": "text", "text": image_ap_system}]},
                                {"role": "user", "content": [{"type": "image_url",
                                                              "image_url": {
                                                                  "url": f"data:image/jpeg;base64,{base64_image}",
                                                                  "detail": "high"}},
                                                             {"type": "text", "text": image_ap_suffix}]}],
                               model=model,
                               max_tokens=50, temperature=0.1)
        print(f"vl model output: \n{llm_output}")
        if not llm_output:
            hallucination_times += 1
            ap = {}
        else:
            result = json_repair.repair_json(llm_output, return_objects=True)
            if not isinstance(result, dict):
                hallucination_times += 1
                ap = {}
            else:
                ap = result

        print(f"ap from image: {ap}")
        print(f"image hallucination times: {hallucination_times}")
        total_analysis_time = time.time() - start_time
        print(f"image analysis finished, total time used: {total_analysis_time}")
"""