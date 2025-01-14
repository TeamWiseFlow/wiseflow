import os
import json
import re
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 获取父目录
sys.path.append(project_root)

from core.scrapers.mp_scraper import mp_scraper

def read_markdown_from_json_files(directory_path):
    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    
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
                markdown = markdown.replace(f'![{alt}]({src})', f'<img>')
            matches = re.findall(link_pattern, markdown)
            for link_text, link_url in matches:
                markdown = markdown.replace(f'[{link_text}]({link_url})', '[url]')
            markdown = [m.strip() for m in markdown.split('# ') if m.strip()]
            markdown = '\n----------------------------------\n'.join(markdown)

            record_file = open(f'{json_file}.txt', 'w', encoding='utf-8')
            record_file.write(markdown)
            record_file.close()

if __name__ == "__main__":
    # Path to the webpage_samples directory
    samples_dir = os.path.dirname(os.path.abspath(__file__)) + "/webpage_samples"
    read_markdown_from_json_files(samples_dir)
