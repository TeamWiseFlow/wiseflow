# -*- coding: utf-8 -*-

# This program requires HTML to be first converted to properly formatted text while preserving link positions and structural information (like crawl4ai's html2text work);
# The complete media list from the webpage needs to be extracted beforehand
# Currently this script only handles images and links, other elements like downloads and videos are not processed yet, todo: process according to media list
# action_dict needs to be extracted from raw html, which is not covered by this script

import os, re
import json
import time
from urllib.parse import urlparse, urljoin


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

common_chars = ',.!;:，；：、一二三四五六七八九十#*@% \t\n\r|*-_…>#'

def normalize_url(url: str, base_url: str) -> str:
    url = url.strip().lower()
    if url.startswith(("javascript:", "mailto:", "javacript:", "tel:", "sms:", "data:", "file:", "ftp:", "about:", "chrome:", "blob:", "ws:", "wss:", "view-source:")):
        return ''
    if "<" in url and url.endswith(">"):
        if '<javascript:void' in url:
            print(url)
        # 暂时应对 crawl4ai 的特殊情况
        part1, part2 = url.split("<")
        if part2.startswith("http"):
            url = part2[:-1]
        else:
            parsed_base = urlparse(part1)
            url = f"{parsed_base.scheme}://{parsed_base.netloc}/{part2[:-1]}"
        
    if url.startswith("www."):
        _url = f"https://{url}"
    elif url.startswith("//"):
        _url = f"https:{url}"
    elif url.startswith(('http:/', 'https:/')):
        _url = url
    elif url.startswith('/'):
        if base_url.endswith('/'):
            _url = base_url[:-1] + url
        else:
            _url = base_url + url
    else:
        _url = urljoin(base_url, url)
    # 处理url中path部分的多余斜杠
    parsed = urlparse(_url)
    path = parsed.path
    # 将连续的多个/替换为单个/
    normalized_path = re.sub(r'/+', '/', path)
    # 重新组装url
    _url = f"{parsed.scheme}://{parsed.netloc}{normalized_path}"
    if parsed.query:
        _url = f"{_url}?{parsed.query}"
    if parsed.fragment:
        _url = f"{_url}#{parsed.fragment}"
    return _url

def deep_scraper(raw_markdown: str, base_url: str, used_img: dict[str, str]) -> tuple[dict, tuple[str, dict]]:
    link_dict = {}
    def check_url_text(text):
        text = text.strip()
        left_bracket = text.find('[')
        right_paren = text.rfind(')')
        
        if -1 in [left_bracket, right_paren] or left_bracket > right_paren:
            return text
        
        # 检查左括号前的文本是否包含至少2个有效字符
        prefix = text[:left_bracket]
        pre_valid_chars = [c for c in prefix if not c.isdigit() and c not in common_chars]
        if len(pre_valid_chars) >= 50:
            return text

        suffix = text[right_paren+1:]
        suf_valid_chars = [c for c in suffix if c not in common_chars]
        if len(pre_valid_chars) >= 2 and len(suf_valid_chars) >= 1:
            return text

        if len(suf_valid_chars) >= 36:
            return text

        # 处理图片标记 ![alt](src)
        img_pattern = r'!\[(.*?)\]\((.*?)\)'
        matches = re.findall(img_pattern, text)
        
        for alt, src in matches:
            # 替换为新格式 §alt||src§
            text = text.replace(f'![{alt}]({src})', f'§{alt}||{src}§')
            
        # 找到所有[part0](part1)格式的片段
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        matches = re.findall(link_pattern, text)
        # 从text中去掉所有matches部分
        for link_text, link_url in matches:
            text = text.replace(f'[{link_text}]({link_url})', '')

        img_marker_pattern = r'§(.*?)\|\|(.*?)§'
        img_marker_matches = re.findall(img_marker_pattern, text)
        alt_img_alt = ""
        alt_img_src = ""
        if img_marker_matches:
            alt_img_alt = img_marker_matches[0][0]
            alt_img_src = img_marker_matches[0][1]
        for alt, src in img_marker_matches:
            text = text.replace(f'§{alt}||{src}§', '')

        text = text.strip()
        
        for link_text, link_url in matches:
            # 处理 \"***\" 格式的片段
            quote_pattern = r'\"(.*?)\"'
            # 提取所有引号包裹的内容
            link_alt = ''.join(re.findall(quote_pattern, link_url))
            if link_alt not in link_text:
                link_text = f"{link_text} {link_alt}"
            # 去掉所有引号包裹的内容
            _url = re.sub(quote_pattern, '', link_url).strip()
            if not _url or _url.startswith('#'):
                continue
            url = normalize_url(_url, base_url)
            if not url:
                continue
            # 检查链接是否是常见文件类型或顶级域名
            has_common_ext = any(url.endswith(ext) for ext in common_file_exts)
            has_common_tld = any(url.endswith(tld) or url.endswith(tld + '/') for tld in common_tlds)
            if has_common_ext or has_common_tld:
                continue

            # 分离§§内的内容和后面的内容
            link_text = link_text.strip()
            inner_matches = re.findall(img_marker_pattern, link_text)
            for alt, src in inner_matches:
                link_text = link_text.replace(f'§{alt}||{src}§', '')
            link_text = link_text.strip()

            if text not in link_text:
                link_text = f"{link_text} {text}"

            # 去除首尾的common_chars和数字
            link_text = link_text.strip(''.join(common_chars + '0123456789'))
            if len(link_text) >= 3:
                if url not in link_dict:
                    link_dict[url] = link_text
                else:
                    if link_dict[url].startswith("§to_be_recognized_by_visual_llm_"):
                        link_dict[url] = link_text
                    else:
                        link_dict[url] = f"{link_dict[url]} {link_text}"

            if url in link_dict:
                continue
            
            img_alt = ""
            img_src = ""
            if inner_matches:
                img_alt = inner_matches[0][0].strip()
                img_src = inner_matches[0][1].strip()

            if not img_src and alt_img_src:
                img_src = alt_img_src
                img_alt = alt_img_alt

            if not img_src or img_src.startswith('#'):
                continue

            img_src = normalize_url(img_src, base_url)
            if not img_src:
                continue
            if any(img_src.endswith(tld) or img_src.endswith(tld + '/') for tld in common_tlds):
                continue
            if any(img_src.endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
                continue
            link_dict[url] = f"{img_alt}§to_be_recognized_by_visual_llm_{img_src}§"
            
        return ''

    texts = raw_markdown.split('\n\n')
    texts = [check_url_text(text) for text in texts]
    texts = [text for text in texts if text.strip()]
    html_text = '\n\n'.join(texts)

    # 处理图片标记 ![alt](src)
    img_pattern = r'(!\[.*?\]\(.*?\))'
    matches = re.findall(img_pattern, html_text)
    for match in matches:
        src = re.search(r'!\[.*?\]\((.*?)\)', match).group(1)
        if src not in used_img:
            html_text = html_text.replace(match, '')
            continue

        alt = used_img[src]
        src = src.strip().lower()
        if not src or src.startswith('#'):
            html_text = html_text.replace(match, alt)
            continue
        src = normalize_url(src, base_url)
        if not src:
            html_text = html_text.replace(match, alt)
            continue

        if any(src.endswith(tld) or src.endswith(tld + '/') for tld in common_tlds):
            html_text = html_text.replace(match, alt)
            continue
        if any(src.endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
            html_text = html_text.replace(match, alt)
            continue
        html_text = html_text.replace(match, f" {alt}§to_be_recognized_by_visual_llm_{src[1:]}§") # to avoid conflict with the url pattern
    
    # 接下来要处理所有的[]()文本了
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    matches = re.findall(link_pattern, html_text)
    text_link_map = {}
    for match in matches:
        link_text, link_url = match
        original_markdown = f'[{link_text}]({link_url})'  # 重建原始的 markdown 链接格式
        # 处理 \"***\" 格式的片段
        quote_pattern = r'\"(.*?)\"'
        # 提取所有引号包裹的内容
        link_alt = ''.join(re.findall(quote_pattern, link_url))
        if link_alt not in link_text:
            link_text = f"{link_text} {link_alt}"
        # 去掉所有引号包裹的内容
        _url = re.sub(quote_pattern, '', link_url).strip()
        if not _url or _url.startswith('#'):
            continue
        url = normalize_url(_url, base_url)
        if not url:
            continue
        key = f"Ref_{len(text_link_map)+1}"
        text_link_map[key] = url

        html_text = html_text.replace(original_markdown, f'{link_text}[{key}]')
    
    # 处理文本中的"野 url"
    url_pattern = r'((?:https?://|www\.)[-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|])'
    matches = re.findall(url_pattern, html_text)
    for url in matches:
        url = normalize_url(url, base_url)
        if not url:
            continue
        key = f"Ref_{len(text_link_map)+1}"
        text_link_map[key] = url
        html_text = html_text.replace(url, f'[{key}]')
    
    # 去掉文本中所有残存的[]和![]
    html_text = html_text.replace('![]', '')  # 去掉![]
    html_text = html_text.replace('[]', '')  # 去掉[]

    return link_dict, (html_text, text_link_map)
        