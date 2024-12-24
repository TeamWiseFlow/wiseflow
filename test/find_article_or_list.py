# -*- coding: utf-8 -*-

import os, re
import json
import time


sample_dir = 'webpage_samples'
list_judge_threshold = 0.007
valid_list_min_length = 10
min_content_length = 420

common_file_exts = [
    'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'svg', 'm3u8',
    'mp4', 'mp3', 'wav', 'avi', 'mov', 'wmv', 'flv', 'webp', 'webm',
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
    'txt', 'csv', 'xls', 'xlsx', 'ppt', 'pptx',
    'json', 'xml', 'yaml', 'yml', 'css', 'js', 'php', 'asp', 'jsp'
]
common_tlds = [
    '.com', '.cn', '.net', '.org', '.edu', '.gov', '.io', '.co',
    '.info', '.biz', '.me', '.tv', '.cc', '.xyz', '.app', '.dev',
    '.cloud', '.ai', '.tech', '.online', '.store', '.shop', '.site',
    '.top', '.vip', '.pro', '.ltd', '.group', '.team', '.work'
]

def find_article_or_list(link_dict, text) -> (bool, bool, str):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    text = '\n'.join(lines)
    text_no_tags = re.sub(r'<\w{1,5}>', '', text)
    text_no_urls = re.sub(r'\[url\d+]', '', text_no_tags)
    content_length = len(text_no_urls)

    valid_url_count = 0
    for url in link_dict.values():
        url_lower = url.lower()
        has_common_ext = any(url_lower.endswith(ext) for ext in common_file_exts)
        has_common_tld = any(url_lower.endswith(tld) or url_lower.endswith(tld + '/') for tld in common_tlds)
        if not has_common_ext and not has_common_tld:
            valid_url_count += 1

    valid_url_rate = valid_url_count / content_length
    is_list = valid_url_rate > 0.007 and valid_url_count > valid_list_min_length
    need_more_info = content_length < min_content_length
    return is_list, need_more_info, text
 

if __name__ == '__main__':
    dirs = os.listdir(sample_dir)
    for _dir in dirs:
        if not _dir.startswith('task'):
            continue
        _path = os.path.join(sample_dir, _dir)
        if not os.path.isdir(_path):
            continue

        samples = os.listdir(_path)
        time_stamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        record_file = os.path.join(_path, f'article_or_list_judge.txt')
        for sample in samples:
            if not os.path.isdir(os.path.join(_path, sample)):
                continue
            files = os.listdir(os.path.join(_path, sample))
            if 'link_dict.json' not in files or 'text.txt' not in files:
                print(f'{sample} files not complete, skip')
                continue
            link_dict = json.load(open(os.path.join(_path, sample, 'link_dict.json'), 'r'))
            text = open(os.path.join(_path, sample, 'text.txt'), 'r').read()
            is_list, need_more_info, text = find_article_or_list(link_dict, text)
            with open(record_file, 'a') as f:
                f.write(f"raw materials: {sample}\n\n")
                f.write(f"cleaned text: \n{text}\n\n")
                f.write("list\n" if is_list else "article\n")
                f.write("need more info\n" if need_more_info else "no need more info\n")
                f.write("*" * 12)
                f.write('\n\n')
