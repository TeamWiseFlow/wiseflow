import os
import json
import re
import sys

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)

from scrapers import mp_scraper

def read_markdown_from_json_files(directory_path):
    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    img_pattern = r'!\[(.*?)\]\(((?:[^()]*|\([^()]*\))*)\)'
    link_pattern = r'\[(.*?)\]\(((?:[^()]*|\([^()]*\))*)\)'
    
    # Process each JSON file
    for json_file in sorted(json_files):
        file_path = os.path.join(directory_path, json_file)
        print(f"\nProcessing file: {json_file}")
        print("-" * 50)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        url = data.get('url')
        if url.startswith('https://mp.weixin.qq.com'):
            result = mp_scraper(data)
            markdown = result.content
        else:
            markdown = data.get('markdown')

        # Find the longest consecutive newlines in the markdown text
        if markdown:
            # 处理图片标记 ![alt](src)
            matches = re.findall(img_pattern, markdown)
            for alt, src in matches:
                # 替换为新格式 §alt||img_12§
                markdown = markdown.replace(f'![{alt}]({src})', '<img>')
            matches = re.findall(link_pattern, markdown)
            for link_text, link_url in matches:
                markdown = markdown.replace(f'[{link_text}]({link_url})', '[url]')
            
            # 使用正则表达式匹配一级标题（行首或行首有空格的"# "），但排除多级标题
            # (?:^|\n) 匹配行首或换行符
            # \s* 匹配零个或多个空白字符
            # (?<!\#) 确保前面不是#（排除多级标题）
            # \# 匹配#字符
            # \s+ 匹配一个或多个空白字符
            sections = re.split(r'(?:^|\n)\s*(?<!\#)\#\s+', markdown)
            markdown_sections = [section.strip() for section in sections if section.strip()]
            
            # 用分隔符连接所有部分
            markdown = '\n*\n----------------------------------\n*\n'.join(markdown_sections)
            record_file = open(f'{json_file}.txt', 'w', encoding='utf-8')
            record_file.write(markdown)
            record_file.close()

if __name__ == "__main__":
    # Path to the webpage_samples directory
    samples_dir = os.path.dirname(os.path.abspath(__file__)) + "/webpage_samples"
    read_markdown_from_json_files(samples_dir)
