import os
import sys
import re

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

# 现在可以直接导入模块，因为core目录已经在Python路径中
from scrapers import *
from agents.get_info import pre_process

def check_url_text(text):
    common_chars = ',.!;:，；：、一二三四五六七八九十#*@% \t\n\r|*-_…>#'
    print(f"processing: {text}")
    left_bracket = text.find('[')
    right_paren = text.rfind(')')
        
    if -1 in [left_bracket, right_paren] or left_bracket > right_paren:
        print("not [] or () marker")
        print(f"left_bracket: {left_bracket}, right_paren: {right_paren}")
        return
        
    # 检查左括号前的文本是否包含至少2个有效字符
    prefix = text[:left_bracket]
    pre_valid_chars = [c for c in prefix if not c.isdigit() and c not in common_chars]
    if len(pre_valid_chars) >= 50:
        print("prefix has at least 50 valid chars")
        print(f"prefix: {prefix}, valid_chars: {pre_valid_chars}")
        return

    suffix = text[right_paren+1:]
    suf_valid_chars = [c for c in suffix if c not in common_chars]
    if len(pre_valid_chars) >= 2 and len(suf_valid_chars) >= 1:
        print("prefix has at least 2 valid chars and suffix has at least 1 valid char")
        print(f"prefix: {prefix}, valid_chars: {pre_valid_chars}, suffix: {suffix}, valid_chars: {suf_valid_chars}")
        return

    if len(suf_valid_chars) >= 36:
        print("suffix has at least 36 valid chars")
        print(f"suffix: {suffix}, valid_chars: {suf_valid_chars}")
        return
        
    print('is a isolated url')

    print("处理图片标记 ![alt](src)")
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(img_pattern, text)
  
    for alt, src in matches:
        # 替换为新格式 <alt||src>
        text = text.replace(f'![{alt}]({src})', f'§{alt}||{src}§')
    print(text)

    print("处理 [part0](part1) 格式的片段")
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    matches = re.findall(link_pattern, text)
    for match in matches:
        print(match)

async def main(html_sample, record_file):
    recognized_img_cache = {}
    parsed_url = urlparse(html_sample['url'])
    domain = parsed_url.netloc
    if domain in custom_scrapers:
        result = custom_scrapers[domain](html_sample)
        raw_markdown = result.content
        used_img = result.images
        title = result.title
        base_url = result.base
        author = result.author
        publish_date = result.publish_date
    else:
        raw_markdown = html_sample['markdown']
        media_dict = html_sample['media'] if html_sample['media'] else {}
        used_img = [d['src'] for d in media_dict.get('images', [])]
        title = ''
        base_url = ''
        author = ''
        publish_date = ''

    if not raw_markdown:
        print(f"no raw_markdown for {file}")
        return

    if not title:
        title = html_sample.get('title', '')
    if not base_url:
        base_url = html_sample.get('base', '')
    if not base_url:
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    print('base_url:', base_url)
            
    if not author:
        author = html_sample.get('author', '')
    if not publish_date:
        publish_date = html_sample.get('publish_date', '')
            
    link_dict, links_parts, contents, recognized_img_cache = await pre_process(raw_markdown, base_url, used_img, recognized_img_cache, test_mode=True)
    result = {
        "link_dict": link_dict,
        "links_part": links_parts,
        "contents": contents,
    }

    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"pre process done, saved to {record_file}")


if __name__ == '__main__':
    import argparse
    import json
    from urllib.parse import urlparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument('--test_file', '-F', type=str, default='')
    parser.add_argument('--sample_dir', '-D', type=str, default='')
    parser.add_argument('--record_folder', '-R', type=str, default='')
    args = parser.parse_args()

    test_file = args.test_file
    sample_dir = args.sample_dir
    record_folder = args.record_folder
    if record_folder:
        os.makedirs(record_folder, exist_ok=True)
    
    files = []
    if test_file:
        files.append(test_file)
    
    if sample_dir:
        files.extend([os.path.join(sample_dir, file) for file in os.listdir(sample_dir)])

    for file in files:
        if not file.endswith('.json'): continue
        print(f"processing {file} ...")
        with open(file, 'r') as f:
            html_sample = json.load(f)
        record_file = os.path.join(record_folder, f'{os.path.basename(file)}_processed.json')
        
        asyncio.run(main(html_sample, record_file))
