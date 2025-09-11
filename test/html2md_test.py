# -*- coding: utf-8 -*-
import os, sys
import json
import asyncio

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

from wis import WeixinArticleMarkdownGenerator, DefaultMarkdownGenerator


async def main(sample: dict, record_file: str):
    url = sample.get("url", "")
    if not url:
        print(f'url is empty, skip')
        return

    html = sample.get("html", "")
    cleaned_html = sample.get("cleaned_html", "")
    metadata = sample.get("metadata", {})
    if "mp.weixin.qq.com" in url:
        markdown_generator = WeixinArticleMarkdownGenerator()
    else:
        markdown_generator = DefaultMarkdownGenerator()
    error_msg, title, author, publish, markdown, link_dict = markdown_generator.generate_markdown(
        raw_html=html,
        cleaned_html=cleaned_html,
        base_url=url,
        metadata=metadata,
    )
    if error_msg:
        print(f'failed: {error_msg}')
        return
    
    print(f'markdown: \n{markdown}')
    result = {
        'url': url,
        'markdown': markdown,
        'link_dict': link_dict,
        'title': title,
        'author': author,
        'published_date': publish
    }
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f'\nsaved to {record_file}\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_dir', '-D', type=str, default='webpage_samples')
    args = parser.parse_args()

    sample_dir = args.sample_dir
    print(f"sample_dir: {sample_dir}")

    for file in os.listdir(sample_dir):
        if not file.endswith('.json'): continue
        if file == 'focus_point.json': continue
        if file.endswith('_processed.json'): continue
        print(f"processing {file} ...\n")
        with open(os.path.join(sample_dir, file), 'r', encoding='utf-8') as f:
            sample = json.load(f)
        
        record_file = os.path.join(sample_dir, f'{file.split(".")[0]}_processed.json')
        asyncio.run(main(sample, record_file))
