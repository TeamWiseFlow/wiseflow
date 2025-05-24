import os, sys
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # get parent dir
sys.path.append(project_root)

from core.tools.openai_wrapper import openai_llm as llm

async def main(task: list):
    vl_model = os.environ.get("VL_MODEL", "")
    if not vl_model:
        print("错误: VL_MODEL not set, will skip extracting info from img, some info may be lost!")
        sys.exit(1)
    cache = {}
    for url in task:
        llm_output = await llm([{"role": "user",
                                "content": [{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
                                                {"type": "text",
                                                "text": "提取图片中的所有文字，如果图片不包含文字或者文字很少或者你判断图片仅是网站logo、商标、图标等，则输出NA。注意请仅输出提取出的文字，不要输出别的任何内容。"}]}],
                                   model=vl_model)
        cache[url] = llm_output
    return cache


if __name__ == '__main__':
    import argparse
    import time
    import json
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument('--test_file', '-F', type=str, default='')
    parser.add_argument('--sample_dir', '-D', type=str, default='')
    args = parser.parse_args()

    test_file = args.test_file
    sample_dir = args.sample_dir

    files = []
    if test_file:
        files.append(test_file)
    
    if sample_dir:
        files.extend([os.path.join(sample_dir, file) for file in os.listdir(sample_dir)])

    for file in files:
        if not file.endswith('sample.json'): continue

        with open(file, 'r') as f:
            sample = json.load(f)
        
        link_dict = sample['link_dict'].copy()
        text = sample['text']

        to_be_replaces = {}
        pattern = r'§to_be_recognized_by_visual_llm_(.*?)§'
        for url, des in link_dict.items():
            matches = re.findall(pattern, des)
            if matches:
                for img_url in matches:
                    # 替换原始描述中的标记
                    des = des.replace(f'§to_be_recognized_by_visual_llm_{img_url}§', img_url)
                    link_dict[url] = des
                    if img_url in to_be_replaces:
                        to_be_replaces[img_url].append(url)
                    else:
                        to_be_replaces[img_url] = [url]

        matches = re.findall(pattern, text)
        if matches:
            for img_url in matches:
                text = text.replace(f'§to_be_recognized_by_visual_llm_{img_url}§', f'h{img_url}')
                img_url = f'h{img_url}'
                if img_url in to_be_replaces:
                    to_be_replaces[img_url].append("content")
                else:
                    to_be_replaces[img_url] = ["content"]

        start_time = time.time()
        print(f"开始提取图片信息")
        result = asyncio.run(main(list(to_be_replaces.keys())))
        end_time = time.time()
        print(f"提取图片信息完成，耗时: {end_time - start_time}秒")

        for img_url, content in result.items():
            for url in to_be_replaces[img_url]:
                if url == "content":
                    text = text.replace(img_url, content)
                else:
                    link_dict[url] = link_dict[url].replace(img_url, content)
        
        if len(link_dict) != len(sample['link_dict']):
            print(f"提取图片信息后，link_dict长度发生变化，原长度: {len(sample['link_dict'])}, 新长度: {len(link_dict)}")
        
        sample['text'] = text
        sample['link_dict'] = link_dict
        new_file = file.replace('.json', '_recognized.json')

        with open(new_file, 'w', encoding='utf-8') as f:
            json.dump(sample, f, indent=4, ensure_ascii=False)
