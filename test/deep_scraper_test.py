import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 获取父目录
sys.path.append(project_root)

from core.utils.deep_scraper import deep_scraper, common_chars, common_file_exts, common_tlds 

test_string = ''

def check_url_text(text):
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


if __name__ == '__main__':
    import argparse
    import time
    import json
    from urllib.parse import urlparse

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

    result_folder = sample_dir if sample_dir else '.'

    for file in files:
        if not file.endswith('.json'): continue

        print(f"processing {file} ...")
        try:
            with open(file, 'r') as f:
                html_sample = json.load(f)
            _url = html_sample['url']
            raw_markdown = html_sample['markdown']
            used_img = {d['src']: d['alt'] for d in html_sample['media']['images']}
        except Exception as e:
            print('sample format error, try to use craw4ai_fething.py to get sample')
            print(f"error: {e}")
            continue

        parsed_url = urlparse(_url)
        domain = parsed_url.netloc
        base_url = f"{parsed_url.scheme}://{domain}"

        time_start = time.time()
        from_html_link_dict, (from_html_text, from_html_text_link_map) = deep_scraper(raw_markdown, base_url, used_img)
        time_end = time.time()
        print(f"time cost for html: {time_end - time_start}s")

        result = {
            "link_dict": from_html_link_dict,
            "text": from_html_text,
            "text_link_map": from_html_text_link_map,
        }
        record_folder = file.replace('.json', '')
        os.makedirs(record_folder, exist_ok=True)
        with open(os.path.join(record_folder, 'sample.json'), 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print("done")
        print("*" * 12)

    if test_string:
        check_url_text(test_string)
        exit()
