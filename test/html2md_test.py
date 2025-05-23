# -*- coding: utf-8 -*-
import os, sys
import json
from datetime import datetime
import asyncio

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(core_path)

from dotenv import load_dotenv
env_path = os.path.join(core_path, 'core', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from core.wwd.markdown_generation_strategy import *
markdown_generation_hub = {'mp.weixin.qq.com': WeixinArticleMarkdownGenerator}
from core.wwd.utils import get_base_domain

async def main(sample: dict, exclude_external_links: bool, record_file: str):
    # cleaned_html = sample["cleaned_html"]
    base_url = sample.get("redirected_url", '') or sample["url"]
    # author = sample["metadata"].get("author", "")
    # title = sample["metadata"].get("title", "")
    published_date = sample["response_headers"].get("last-modified", "")
    domain = get_base_domain(base_url)
    markdown_generator = markdown_generation_hub.get(domain, DefaultMarkdownGenerator)()
    error_msg, title, author, publish, markdown, link_dict = (
        await markdown_generator.generate_markdown(
            raw_html=sample["html"],
            cleaned_html=sample["cleaned_html"],
            base_url=base_url,
            metadata=sample["metadata"],
            exclude_external_links=exclude_external_links,
        )
    )
    if error_msg:
        print(f'failed: {error_msg}')
        return
    
    print(f'markdown: \n{markdown}')
    result = {
        'url': base_url,
        'markdown': markdown,
        'link_dict': link_dict,
        'title': title,
        'author': author,
        'published_date': publish or published_date
    }
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f'\nsaved to {record_file}\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_dir', '-D', type=str, default='webpage_samples')
    parser.add_argument('--exclude_external_links', '-E', type=bool, default=False)
    args = parser.parse_args()

    sample_dir = args.sample_dir
    print(f"sample_dir: {sample_dir}")
    exclude_external_links = args.exclude_external_links

    for file in os.listdir(sample_dir):
        if not file.endswith('.json'): continue
        if file == 'focus_point.json': continue
        if file.endswith('_processed.json'): continue
        print(f"processing {file} ...\n")
        with open(os.path.join(sample_dir, file), 'r') as f:
            sample = json.load(f)
        
        record_file = os.path.join(sample_dir, f'{file.split(".")[0]}_processed.json')
        asyncio.run(main(sample, exclude_external_links, record_file))
