from __future__ import annotations

from bs4 import BeautifulSoup
import regex as re
from crawl4ai import CrawlResult
from .scraper_data import ScraperResultData

# 定义所有可能包含文本的块级和内联元素
text_elements = {
    # 块级元素
    'div', 'section', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    # 内联文本元素
    'span', 'em', 'strong'
}


def mp_scraper(fetch_result: CrawlResult | dict) -> ScraperResultData:
    if isinstance(fetch_result, dict):
        url = fetch_result['url']
        raw_html = fetch_result['html']
        cleaned_html = fetch_result['cleaned_html']
        raw_markdown = fetch_result['markdown']
        media = fetch_result['media']['images']
        metadata = fetch_result['metadata']
    elif isinstance(fetch_result, CrawlResult):
        url = fetch_result.url
        raw_html = fetch_result.html
        cleaned_html = fetch_result.cleaned_html
        raw_markdown = fetch_result.markdown
        media = fetch_result.media['images']
        metadata = fetch_result.metadata
    else:
        raise TypeError('fetch_result must be a CrawlResult or a dict')

    content = ''
    images = []

    if url.startswith('https://mp.weixin.qq.com/mp/appmsgalbum'):
        # album page type
        soup = BeautifulSoup(raw_html, 'html.parser')
        for li in soup.find_all('li', class_='album__list-item'):
            u_text = li.get_text(strip=True)
            u_title = li.attrs['data-title'].strip()
            _url = li.attrs['data-link'].replace("http://", "https://", 1)
            if not _url or _url.startswith('javas') or _url.startswith('#') or _url.startswith('mailto:') or _url.startswith('data:') or _url.startswith('about:blank'):
                continue

            cut_off_point = _url.find('chksm=')
            if cut_off_point != -1:
                _url = _url[:cut_off_point - 1]
            
            if u_title in u_text:
                description = u_text
            else:
                description = f'{u_title}-{u_text}'
            content += f'[{description}]({_url})\n'
        return ScraperResultData(content=content, images=images)
 
    def process_content(content_div):
        # 3.1 处理所有 <img> 元素
        for img in content_div.find_all('img', attrs={'data-src': True}, recursive=True):
            data_type = img.get('data-type', '')
            if data_type in ['gif', 'svg']:
                continue
            src = img.get('data-src')
            if not src or src.startswith('#') or src.startswith('about:blank'):
                src = None
            text = img.get('alt', '').strip()
            if not src:
                img.replace_with(text)
                continue
            images.append(src)
            # find all area urls related to this img
            area_urls = set()
            if img.get('usemap'):
                # remove the # at the beginning of the map name
                map_name = img.get('usemap').lstrip('#')
                # find the map tag
                map_tag = content_div.find('map', {'name': map_name})
                if map_tag:
                    # get all area tags under the map
                    for area in map_tag.find_all('area', href=True):
                        area_href = area.get('href')
                        area_urls.add(area_href)
                        area.decompose()
                    # delete the whole map tag
                    map_tag.decompose()
            area_urls = ')[]('.join(area_urls)
            replacement_text = f'![{text}]({src})[]({area_urls})' if area_urls else f'![{text}]({src})'
            img.replace_with(replacement_text)

        for media in content_div.find_all(['video', 'audio', 'source', 'embed', 'iframe', 'figure'], src=True, recursive=True):
            src = media.get('src')
            if not src or src.startswith('javascript:') or src.startswith('#') or src.startswith('mailto:') or src.startswith('data:') or src.startswith('about:blank'):
                src = None
            text = media.get_text().strip() or media.get('alt', '').strip()
            if src:
                media.replace_with(f"[{text}]({src})")
            else:
                media.decompose()
        
        for obj in content_div.find_all('object', data=True, recursive=True):
            data = obj.get('data')
            if not data or data.startswith('javascript:') or data.startswith('#') or data.startswith('mailto:') or data.startswith('data:') or data.startswith('about:blank'):
                data = None
            text = obj.get_text().strip() or obj.get('alt', '').strip()
            if data:
                obj.replace_with(f"[{text}]({data})")
            else:
                obj.decompose()
        
        # process links at last, so that we can keep the image and media info in the link
        for a in content_div.find_all('a', href=True, recursive=True):
            href = a.get('href')
            if not href or href.startswith('javascript:') or href.startswith('#') or href.startswith('about:blank'):
                href = None
            text = a.get_text().strip()
            if href:
                a.replace_with(f"[{text}]({href})")
            else:
                a.decompose()

        # handle lists
        for list_tag in content_div.find_all(['ul', 'ol'], recursive=True):
            list_text = []
            for idx, item in enumerate(list_tag.find_all('li')):
                list_text.append(f"{idx + 1}. {item.get_text().strip()}")
            list_text = '\t'.join(list_text)
            list_tag.replace_with(f"{list_text}\n")
        
        # handle strikethrough text
        for del_tag in content_div.find_all(['del', 's'], recursive=True):
            del_text = del_tag.get_text().strip()
            if del_text:
                del_tag.replace_with(f"{del_text}(maybe_outdated)")
            else:
                del_tag.decompose()
        
        # handle tables
        for table in content_div.find_all('table', recursive=True):
            table_text = []
            
            # handle caption
            caption = table.find('caption')
            if caption:
                table_text.append(caption.get_text().strip())
            
            # get headers
            headers = []
            for th in table.find_all('th'):
                headers.append(th.get_text().strip())
            
            # handle all rows (including tbody and tfoot)
            for row in table.find_all('tr'):
                # get the first cell value
                # try to find th as first_val
                first_cell = row.find(['th', 'td'])
                if not first_cell:
                    continue
                first_val = first_cell.get_text().strip()
                cells = row.find_all('td')
                if not cells:
                    continue
                # handle remaining cells
                for idx, cell in enumerate(cells):
                    cell_text = cell.get_text().strip()
                    if not cell_text or cell_text == first_val:
                        continue
  
                    header_text = headers[idx] if idx < len(headers) else ''
                    cell_str = f"{first_val}-{header_text}-{cell_text}"
                    table_text.append(cell_str)
            
            # replace the table with the processed text
            table_text = '\n'.join(table_text)
            table.replace_with(f"\n{table_text}\n")

        # 3.3 按照子元素获取文本内容，统一换行
        content_parts = []
        for element in content_div.children:
            if element.name in ['br', 'br/', 'br /', 'hr', 'hr/', 'hr /', 'wbr']:
                content_parts.append('\n')
            elif element.name in text_elements:
                text = element.get_text(strip=True)
                if text:
                    content_parts.append(text)
                # 只在块级元素后添加换行符
                if element.name in {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                    content_parts.append('\n')
                if element.name in {'div', 'section'}:
                    content_parts.append('# ')
            elif isinstance(element, str):
                text = element.strip()
                if text:
                    content_parts.append(text)
    
        return ''.join(content_parts).strip()

    soup = BeautifulSoup(cleaned_html, 'html.parser')

    # 1. 查找第一个包含 <h1> 元素的 div 块，提取 title
    h1_tag = soup.find('h1')
    if h1_tag:
        h1_div = h1_tag.parent
        title = h1_tag.get_text(strip=True)
    else:
        # 如果找不到的话 说明是已删除或者分享页
        soup = BeautifulSoup(raw_html, 'html.parser')
        # 从 original_panel_tool 中找到 data-url
        share_source = soup.find('span', id='js_share_source')
        if share_source and share_source.get('data-url'):
            data_url = share_source['data-url']
            # 替换 http 为 https
            data_url = data_url.replace('http://', 'https://', 1)
            if not data_url or not data_url.startswith('https://mp.weixin.qq.com'):
                # maybe a new_type_article
                return ScraperResultData(title='maybe a new_type_article', content='new_type_article, type 4')
            # 从 js_content 中获取描述文本
            content_div = soup.find('div', id='js_content')
            if not content_div:
                # maybe a new_type_article
                return ScraperResultData(title='maybe a new_type_article', content='new_type_article, type 3')
            des = content_div.get_text(strip=True)
            return ScraperResultData(content=f'[{des}]({data_url})')
        else:
            # a deleted page
            return ScraperResultData()
    
    # 2. 判断这个子块下面包含几个非空 div 子块
    sub_divs = [div for div in h1_div.find_all('div', recursive=False) if len(div.contents) > 0]
    num_sub_divs = len(sub_divs)
        
    if num_sub_divs == 1:
        # 2.1 如果只包含一个子块
        strong_tag = sub_divs[0].find('strong')
        if strong_tag:
            author = strong_tag.get_text(strip=True)
            # 查找包含日期和时间的span标签
            date_span = sub_divs[0].find('span', string=re.compile(r'\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}'))
            # 如果找到日期，只提取日期部分
            if date_span:
                publish_date = date_span.get_text(strip=True).split()[0]  # 只取日期部分
            else:
                publish_date = None
                return ScraperResultData(title='maybe a new_type_article', content='new_type_article, type 2')
            # 提取与包含 <h1> 元素的 div 块平级的紧挨着的下一个 div 块作为 content
            content_div = h1_div.find_next_sibling('div')
            if not content_div:
                content = raw_markdown
            else:
                content = title + '\n\n' + process_content(content_div)
        else:
            author = None
            publish_date = None
            content = raw_markdown
            images = [d['src'] for d in media]
            
    elif num_sub_divs >= 2:
        # 2.2 如果包含两个及以上子块
        a_tag = sub_divs[0].find('a', href="javascript:void(0);")
        if a_tag:
            author = a_tag.get_text(strip=True)
            # 查找下一个包含日期时间的em标签
            date_em = sub_divs[0].find('em', string=re.compile(r'\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}'))
            if date_em:
                # 只提取日期部分
                publish_date = date_em.get_text(strip=True).split()[0]
            else:
                publish_date = None
                title = 'maybe a new_type_article'
            # 剩下的 div 子块合起来作为 content
            content_divs = sub_divs[1:]
            content = '# '.join([process_content(div) for div in content_divs])
            content = title + '\n\n' + content
        else:
            # 2025-03-17 found
            # a photo-alumbs page, just get every link with the description, formate as [description](url) as the content
            des = metadata.get('description', '')
            # 使用正则表达式匹配所有的链接和描述对
            pattern = r'href=\\x26quot;(.*?)\\x26quot;.*?\\x26gt;(.*?)\\x26lt;/a'
            matches = re.findall(pattern, des)
            # 处理每个匹配项
            for url, description in matches:
                # 清理URL中的转义字符
                cleaned_url = clean_weixin_url(url)
                # 添加到内容中，格式为 [描述](URL)
                content += f'[{description.strip()}]({cleaned_url})\n'

            if not content:
                # this is a album page, just use the markdown
                # return ScraperResultData(title='maybe a new_type_article', content='new_type_article, type 1')
                content = raw_markdown

            return ScraperResultData(title=title, content=content)
    else:
        author = None
        publish_date = None
        content = 'new_type_article, type 0'

    if len(images) > 2:
        images = images[1:-1]
    return ScraperResultData(title=title, content=content, images=images, author=author, publish_date=publish_date)


def clean_weixin_url(url):
    """
    清理微信URL，将转义字符替换为正常字符
    
    Args:
        url (str): 包含转义字符的微信URL
        
    Returns:
        str: 清理后的URL
    """
    # 替换常见的转义序列
    replacements = {
        '\\x26amp;amp;': '&',
        '\\x26amp;': '&',
        '\\x26quot': '',
        '\\x26': '&'
    }
    
    for old, new in replacements.items():
        url = url.replace(old, new)
    
    return url
