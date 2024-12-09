# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
import os, re
import logging


project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

log_formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create logger and set level to debug
logger = logging.getLogger('mp_scraper')
logger.handlers = []
logger.setLevel('DEBUG')
logger.propagate = False

# create file handler and set level to debug
file = os.path.join(project_dir, 'mp_scraper.log')
file_handler = logging.FileHandler(file, 'a', encoding='utf-8')
file_handler.setLevel('INFO')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# create console handler and set level to info
console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

async def mp_scraper(html: str, url: str) -> tuple[dict, set, list]:
    if not url.startswith('https://mp.weixin.qq.com') and not url.startswith('http://mp.weixin.qq.com'):
        logger.warning(f'{url} is not a mp url, you should not use this function')
        return {}, set(), []

    url = url.replace("http://", "https://", 1)
    soup = BeautifulSoup(html, 'html.parser')

    if url.startswith('https://mp.weixin.qq.com/mp/appmsgalbum'):
        # 文章目录
        urls = {li.attrs['data-link'].replace("http://", "https://", 1) for li in soup.find_all('li', class_='album__list-item')}
        simple_urls = set()
        for url in urls:
            cut_off_point = url.find('chksm=')
            if cut_off_point != -1:
                url = url[:cut_off_point - 1]
            simple_urls.add(url)
        return {}, simple_urls, []

        # Get the original release date first
    pattern = r"var createTime = '(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}'"
    match = re.search(pattern, html)
    if match:
        publish_time = match.group(1)
    else:
        publish_time = datetime.strftime(datetime.today(), "%Y-%m-%d")

    # Get description content from < meta > tag
    try:
        meta_description = soup.find('meta', attrs={'name': 'description'})
        summary = meta_description['content'].strip() if meta_description else ''
        # card_info = soup.find('div', id='img-content')
        # Parse the required content from the < div > tag
        rich_media_title = soup.find('h1', id='activity-name').text.strip() \
            if soup.find('h1', id='activity-name') \
            else soup.find('h1', class_='rich_media_title').text.strip()
        profile_nickname = soup.find('div', class_='wx_follow_nickname').text.strip()
    except Exception as e:
        logger.warning(f"not mp format: {url}\n{e}")
        # For mp.weixin.qq.com types, mp_crawler won't work, and most likely neither will the other two
        return {}, set(), []

    if not rich_media_title or not profile_nickname:
        logger.warning(f"failed to analysis {url}, no title or profile_nickname")
        return {}, set(), []

    # Parse text and image links within the content interval
    # because the structure of this part is completely different, and a separate analysis scheme needs to be written
    # (but the proportion of this type of article is not high).
    texts = []
    content_area = soup.find('div', id='js_content')
    if content_area:
        # 提取文本
        for section in content_area.find_all(['section', 'p'], recursive=False):  # 遍历顶级section
            text = section.get_text(separator=' ', strip=True)
            if text and text not in texts:
                texts.append(text)
        cleaned_texts = [t for t in texts if t.strip()]
        content = '\n'.join(cleaned_texts)
    else:
        logger.warning(f"failed to analysis contents {url}")
        return {}, set(), []
    if content:
        content = f"[from {profile_nickname}]{content}"
    else:
        # If the content does not have it, but the summary has it, it means that it is a mp of the picture sharing type.
        # At this time, you can use the summary as the content.
        content = f"[from {profile_nickname}]{summary}"

    article = {'author': profile_nickname,
               'publish_date': publish_time,
               'content': content}

    return article, set(), []
