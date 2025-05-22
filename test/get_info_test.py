# -*- coding: utf-8 -*-
import os, sys
import json
import time
from datetime import datetime
import re

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(core_path)

from dotenv import load_dotenv
env_path = os.path.join(core_path, 'core', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from core.wwd import MaxLengthChunking, LLMExtractionStrategy

benchmark_model = 'Qwen/Qwen3-14B'
models = []

def main(focus_point: dict, sections: list, sample: dict, date_stamp: str, record_file: str):
    raw_markdown = '\n'.join(sections)
    url = sample.get("url", "")
    link_dict = sample.get("link_dict", {})
    author = sample.get("author", "")
    published_date = sample.get("published_date", "")
    title = sample.get("title", "")
    for model in [benchmark_model] + models:
        contents = sections.copy()
        extractor = LLMExtractionStrategy(model=model,
                                          # schema=schema,
                                          focuspoint=focus_point['focuspoint'],
                                          restrictions=focus_point['explanation'],
                                          verbose=True)
        # if model == benchmark_model:
            # print('prompt template:')
            # print(extractor.prompt)
            # print('\n')
        print(f"running {model} ...")
        start_time = time.time()
        extracted_content = extractor.run(url='sample', 
                                          sections=contents, 
                                          title=title, 
                                          author=author, 
                                          published_date=published_date, 
                                          date_stamp=date_stamp)
        time_cost = int((time.time() - start_time) * 1000) / 1000
        print(f"time cost: {time_cost}s")
        more_links = set()
        infos = []
        hallucination_times = 0
        total_parsed = 0
        for block in extracted_content:
            results = block.get("links", [])
            for result in results:
                result = result.strip()
                if not result: continue
                more_links.add(result)
                links = re.findall(r'\[\d+]', result)
                total_parsed += len(links)
                for link in links:
                    if link not in link_dict:
                        hallucination_times += 1

            results = block.get("info", [])
            for res in results:
                res = res.strip()
                if not res: continue
                url_tags = re.findall(r'\[\d+]', res)
                for _tag in url_tags:
                    total_parsed += 1
                    if _tag not in link_dict and _tag not in raw_markdown:
                        hallucination_times += 1
                        res += f' (hallucination: {_tag})'
                infos.append(res)

        hallucination_rate = round((hallucination_times / total_parsed) * 100, 2) if total_parsed > 0 else 'NA'
        print(f"hallucination rate: {hallucination_rate} %")
        more_links_text = ''
        for idx, link in enumerate(more_links):
            more_links_text += f"{idx+1}. {link}\n\n"
        infos_text = ''
        for idx, info in enumerate(infos):
            infos_text += f"{idx+1}. {info}\n\n"

        Completion_tokens = extractor.total_usage.completion_tokens
        Prompt_tokens = extractor.total_usage.prompt_tokens
        Total_tokens = extractor.total_usage.total_tokens
        with open(record_file, 'a') as f:
            f.write(f"model: {model}\n")
            f.write(f"time cost: {time_cost}s\n")
            f.write(f"tokens usage: {Total_tokens} (completion: {Completion_tokens}, prompt: {Prompt_tokens})\n\n")
            f.write(f"hallucination times: {hallucination_times}\n")
            f.write(f"hallucination rate: {hallucination_rate} %\n\n")
            f.write(f"related urls: \n{more_links_text}\n")
            f.write(f"related infos: \n{infos_text}\n")
            f.write('\n\n')

        print('\n\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_dir', '-D', type=str, default='webpage_samples')
    parser.add_argument('--include_ap', '-I', type=bool, default=False)
    args = parser.parse_args()

    sample_dir = args.sample_dir
    print(f"sample_dir: {sample_dir}")
    include_ap = args.include_ap
    if not os.path.exists(os.path.join(sample_dir, 'focus_point.json')):
        raise ValueError(f'{sample_dir} focus_point.json not found')
    
    focus_point = json.load(open(os.path.join(sample_dir, 'focus_point.json'), 'r'))
    date_stamp = '2025-04-27'
    chunking = MaxLengthChunking()
    time_stamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    record_file = os.path.join(sample_dir, f'record-{time_stamp}.txt')
    with open(record_file, 'w') as f:
        f.write(f"focus statement: \n{focus_point}\n\n")

    for file in os.listdir(sample_dir):
        if not file.endswith('_processed.json'): continue
        print(f"processing {file} ...\n")
        with open(os.path.join(sample_dir, file), 'r') as f:
            sample = json.load(f)
        sections = chunking.chunk(sample.pop("markdown"))
        with open(record_file, 'a') as f:
            f.write(f"raw materials: {file}\n\n")
            f.write(f"url: {sample['url']}\n")
        main(focus_point, sections, sample, date_stamp, record_file)
