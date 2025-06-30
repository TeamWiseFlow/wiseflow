# -*- coding: utf-8 -*-
import os, sys
import json
import time
from datetime import datetime
import re

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from wis import MaxLengthChunking, LLMExtractionStrategy
from async_logger import wis_logger

models = ['Qwen/Qwen3-14B', 'Qwen/Qwen3-32B']

def main(sample: dict, 
         record_file: str,
         date_stamp: str,
         chunking: MaxLengthChunking,
         extractor: LLMExtractionStrategy = None):
    
    sections = chunking.chunk(sample.get("markdown", ""))
    url = sample.get("url", "")
    title = sample.get("title", "")
    author = sample.get("author", "")
    published_date = sample.get("published_date", "")
    link_dict = sample.get("link_dict", {})

    for model in models:
        print(f"testing {model} ...\n")
        t1 = time.perf_counter()
        extracted_content = extractor.run(sections=sections,
                                          url=url,
                                          title=title,
                                          author=author,
                                          publish_date=published_date,
                                          mode='both' if link_dict else 'only_info',
                                          date_stamp=date_stamp,
                                          model=model,
                                          link_dict=link_dict)
        t2 = time.perf_counter()
        time_cost = t2 - t1

        Completion_tokens = extractor.total_usage.completion_tokens
        Prompt_tokens = extractor.total_usage.prompt_tokens
        Total_tokens = extractor.total_usage.total_tokens
        if not extractor.schema_mode:
            links_text = '\n'.join(extracted_content[0]['links'])
            infos_text = ''
            for results in extracted_content[0]['infos']:
                infos_text += f"{results['content']}\n"
            result_text = f"### related urls: \n{links_text}\n\n### related infos: \n{infos_text}\n"
        else:
            result_text = json.dumps(extracted_content, indent=4, ensure_ascii=False)

        with open(record_file, 'a') as f:
            f.write(f"## model: {model}\n")
            f.write(f"time cost: {time_cost}s\n")
            f.write(f"tokens usage: {Total_tokens} (completion: {Completion_tokens}, prompt: {Prompt_tokens})\n\n")
            f.write(result_text)
            f.write('\n\n')

        print('\n\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_dir', '-D', type=str, default='webpage_samples')
    args = parser.parse_args()

    sample_dir = args.sample_dir
    print(f"sample_dir: {sample_dir}")
    if not os.path.exists(os.path.join(sample_dir, 'focus_point.json')):
        raise ValueError(f'{sample_dir} focus_point.json not found')
    
    with open(os.path.join(sample_dir, 'focus_point.json'), 'r') as f:
        focus_point = json.load(f)
    role = focus_point.get('role', '')
    purpose = focus_point.get('purpose', '')
    focuspoint = focus_point.get('focuspoint', '')
    restrictions = focus_point.get('restrictions', '')
    explanation = focus_point.get('explanation', '')
    schema = focus_point.get('schema', '')

    if schema:
        extractor = LLMExtractionStrategy(schema=schema, verbose=True, logger=wis_logger)
    else:
        extractor = LLMExtractionStrategy(focuspoint=focuspoint, 
                                          restrictions=restrictions, 
                                          explanation=explanation,
                                          role=role, 
                                          purpose=purpose, 
                                          verbose=True,
                                          logger=wis_logger)
    
    chunking = MaxLengthChunking()
    
    date_stamp = '2025-04-27'
    time_stamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    record_file = os.path.join(sample_dir, f'record-{time_stamp}.txt')
    with open(record_file, 'w') as f:
        f.write(f"focus statement: \n{focus_point}\n\n")
    for file in os.listdir(sample_dir):
        if not file.endswith('_processed.json'): continue
        print(f"processing {file} ...\n")
        with open(os.path.join(sample_dir, file), 'r') as f:
            sample = json.load(f)
        with open(record_file, 'a') as f:
            f.write(f"# raw materials: {file}\n")
            f.write(f"url: {sample['url']}\n\n")
        main(sample, record_file, date_stamp, chunking, extractor)
