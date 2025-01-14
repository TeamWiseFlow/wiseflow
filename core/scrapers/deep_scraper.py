# -*- coding: utf-8 -*-

# This program requires HTML to be first converted to properly formatted text while preserving link positions and structural information (like crawl4ai's html2text work);
# The complete media list from the webpage needs to be extracted beforehand
# Currently this script only handles images and links, other elements like downloads and videos are not processed yet, todo: process according to media list
# action_dict needs to be extracted from raw html, which is not covered by this script

import re
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
    url = url.strip()
    if url.startswith(('www.', 'WWW.')):
        _url = f"https://{url}"
    elif url.startswith('/www.'):
        _url = f"https:/{url}"
    elif url.startswith("//"):
        _url = f"https:{url}"
    elif url.startswith(('http://', 'https://')):
        _url = url
    elif url.startswith('http:/'):
        _url = f"http://{url[6:]}"
    elif url.startswith('https:/'):
        _url = f"https://{url[7:]}"
    else:
        _url = urljoin(base_url, url)
    
    _ss = _url.split('//')
    if len(_ss) == 2:
        return '//'.join(_ss)
    else:
        return _ss[0] + '//' + '/'.join(_ss[1:])


def deep_scraper(raw_markdown: str, base_url: str, used_img: list[str]) -> tuple[dict, list[str], dict]:
    link_dict = {}
    to_be_recognized_by_visual_llm = {}
    def check_url_text(text):
        # text = text.strip()
        # for special url formate from crawl4ai 0.4.247
        text = re.sub(r'<javascript:.*?>', '<javascript:>', text).strip()

        # 处理图片标记 ![alt](src)
        img_pattern = r'(!\[(.*?)\]\((.*?)\))'
        matches = re.findall(img_pattern, text)
        for _sec,alt, src in matches:
            # 替换为新格式 §alt||src§
            text = text.replace(_sec, f'§{alt}||{src}§', 1)  
            
        # 找到所有[part0](part1)格式的片段
        link_pattern = r'(\[(.*?)\]\((.*?)\))'
        matches = re.findall(link_pattern, text)
        for _sec, link_text, link_url in matches:
            print("found link sec:", _sec)
            # 处理 \"***\" 格式的片段
            quote_pattern = r'\"(.*?)\"'
            # 提取所有引号包裹的内容
            _title = ''.join(re.findall(quote_pattern, link_url))

            # 分离§§内的内容和后面的内容
            img_marker_pattern = r'§(.*?)\|\|(.*?)§'
            inner_matches = re.findall(img_marker_pattern, link_text)
            for alt, src in inner_matches:
                link_text = link_text.replace(f'§{alt}||{src}§', '')
            link_text = link_text.strip()
            if _title not in link_text:
                link_text = f"{_title} - {link_text}"
            
            link_text = link_text.strip()
            if not link_text and inner_matches:
                img_alt = inner_matches[0][0].strip()
                img_src = inner_matches[0][1].strip()
                if img_src and not img_src.startswith('#'):
                    img_src = normalize_url(img_src, base_url)
                    if not img_src:
                        link_text = img_alt
                    elif len(img_alt) > 2:
                        _key = f"[img{len(link_dict)+1}]"
                        link_dict[_key] = img_src
                        link_text = img_alt + _key
                    elif any(img_src.endswith(tld) or img_src.endswith(tld + '/') for tld in common_tlds):
                        _key = f"[img{len(link_dict)+1}]"
                        link_dict[_key] = img_src
                        link_text = img_alt + _key
                    elif any(img_src.endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
                        _key = f"[img{len(link_dict)+1}]"
                        link_dict[_key] = img_src
                        link_text = img_alt + _key
                    else:
                        if img_src not in to_be_recognized_by_visual_llm:
                            to_be_recognized_by_visual_llm[img_src] = f"§{len(to_be_recognized_by_visual_llm)+1}§"
                        _key = f"[img{len(link_dict)+1}]"
                        link_dict[_key] = img_src
                        link_text = to_be_recognized_by_visual_llm[img_src] + _key
                else:
                    link_text = img_alt

            real_url_pattern = r'<(.*?)>'
            real_url = re.search(real_url_pattern, link_url)
            if real_url:
                _url = real_url.group(1).strip()
            else:
                _url = re.sub(quote_pattern, '', link_url).strip()

            if not _url or _url.startswith(('#', 'javascript:')):
                text = text.replace(_sec, link_text, 1)
                continue
            url = normalize_url(_url, base_url)
            _key = f"[{len(link_dict)+1}]"
            link_dict[_key] = url
            text = text.replace(_sec, link_text + _key, 1)

            # 检查链接是否是常见文件类型或顶级域名
            # todo: get_more_url 时再处理
            """
            has_common_ext = any(url.endswith(ext) for ext in common_file_exts)
            has_common_tld = any(url.endswith(tld) or url.endswith(tld + '/') for tld in common_tlds)
            if has_common_ext or has_common_tld:
                continue
            """
        # 处理文本中的其他图片标记
        img_pattern = r'(§(.*?)\|\|(.*?)§)'
        matches = re.findall(img_pattern, text)
        for _sec, alt, src in matches:
            if not src or src.startswith('#') or src not in used_img:
                text = text.replace(_sec, alt, 1)
                continue
            img_src = normalize_url(src, base_url)
            if not img_src:
                text = text.replace(_sec, alt, 1)
            elif len(alt) > 2:
                _key = f"[img{len(link_dict)+1}]"
                link_dict[_key] = img_src
                text = text.replace(_sec, alt + _key, 1)
            elif any(img_src.endswith(tld) or img_src.endswith(tld + '/') for tld in common_tlds):
                _key = f"[img{len(link_dict)+1}]"
                link_dict[_key] = img_src
                text = text.replace(_sec, alt + _key, 1)
            elif any(img_src.endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
                _key = f"[img{len(link_dict)+1}]"
                link_dict[_key] = img_src
                text = text.replace(_sec, alt + _key, 1)
            else:
                if img_src not in to_be_recognized_by_visual_llm:
                    to_be_recognized_by_visual_llm[img_src] = f"§{len(to_be_recognized_by_visual_llm)+1}§"
                _key = f"[img{len(link_dict)+1}]"
                link_dict[_key] = img_src
                text = text.replace(_sec, to_be_recognized_by_visual_llm[img_src] + _key, 1)

        # 处理文本中的"野 url"
        url_pattern = r'((?:https?://|www\.)[-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|])'
        matches = re.findall(url_pattern, text)
        for url in matches:
            url = normalize_url(url, base_url)
            _key = f"[{len(link_dict)+1}]"
            link_dict[_key] = url
            text = text.replace(url, _key, 1)

        return text

    sections = raw_markdown.split('# ') # use '# ' to avoid # in url
    texts = [check_url_text(text) for text in sections]
    texts = [text for text in texts if text.strip()]

    return link_dict, texts, to_be_recognized_by_visual_llm
        