import os
import json
import re

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
                
        markdown = data.get('markdown')
        # Find the longest consecutive newlines in the markdown text
        if markdown:
            # Find all sequences of newlines and get their lengths
            max_newlines = max(len(match) for match in re.findall(r'\n+', markdown)) if re.search(r'\n+', markdown) else 0
            print(f"Longest consecutive newlines: {max_newlines}")
            if max_newlines < 2:
                sections = [markdown]
            else:
                sections = markdown.split('\n' * max_newlines)

            for i, section in enumerate(sections):
                print(f"Section {i + 1}:")
                print(section)
                print('\n\n')
                newline_count = section.count('\n')
                # 处理图片标记 ![alt](src)
                img_pattern = r'!\[(.*?)\]\((.*?)\)'
                matches = re.findall(img_pattern, section)
                for alt, src in matches:
                # 替换为新格式 §alt||src§
                    section = section.replace(f'![{alt}]({src})', f'§{alt}||{src}§')
                # 处理链接标记 [text](url)
                matches = re.findall(link_pattern, section)
                # 从text中去掉所有matches部分
                for link_text, link_url in matches:
                    section = section.replace(f'[{link_text}]({link_url})', '')
                
                if len(section) == 0:
                    print("no text in section")
                    continue
                print(f"newline/text ratio: {newline_count/len(section)*100}")
                print(f"links/section ratio: {len(matches)/len(section)*100}")
                print("-" * 50)


if __name__ == "__main__":
    # Path to the webpage_samples directory
    samples_dir = os.path.dirname(os.path.abspath(__file__)) + "/webpage_samples"
    read_markdown_from_json_files(samples_dir)
