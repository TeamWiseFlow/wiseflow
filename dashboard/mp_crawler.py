import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re


header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/604.1 Edg/112.0.100.0'}


def mp_crawler(url: str, logger) -> (int, dict):
    if not url.startswith('https://mp.weixin.qq.com') and not url.startswith('http://mp.weixin.qq.com'):
        logger.warning(f'{url} is not a mp url, you should not use this function')
        return -5, {}

    url = url.replace("http://", "https://", 1)

    try:
        with httpx.Client() as client:
            response = client.get(url, headers=header, timeout=30)
    except Exception as e:
        logger.warning(f"cannot get content from {url}\n{e}")
        return -7, {}

    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the original release date first
    pattern = r"var createTime = '(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}'"
    match = re.search(pattern, response.text)

    if match:
        date_only = match.group(1)
        publish_time = date_only.replace('-', '')
    else:
        publish_time = datetime.strftime(datetime.today(), "%Y%m%d")

    # Get description content from < meta > tag
    try:
        meta_description = soup.find('meta', attrs={'name': 'description'})
        summary = meta_description['content'].strip() if meta_description else ''
        card_info = soup.find('div', id='img-content')
        # Parse the required content from the < div > tag
        rich_media_title = soup.find('h1', id='activity-name').text.strip() \
            if soup.find('h1', id='activity-name') \
            else soup.find('h1', class_='rich_media_title').text.strip()
        profile_nickname = card_info.find('strong', class_='profile_nickname').text.strip() \
            if card_info \
            else soup.find('div', class_='wx_follow_nickname').text.strip()
    except Exception as e:
        logger.warning(f"not mp format: {url}\n{e}")
        return -7, {}

    if not rich_media_title or not profile_nickname:
        logger.warning(f"failed to analysis {url}, no title or profile_nickname")
        # For mp.weixin.qq.com types, mp_crawler won't work, and most likely neither will the other two
        return -7, {}

    # Parse text and image links within the content interval
    # Todo This scheme is compatible with picture sharing MP articles, but the pictures of the content cannot be obtained,
    #  because the structure of this part is completely different, and a separate analysis scheme needs to be written
    #  (but the proportion of this type of article is not high).
    texts = []
    images = set()
    content_area = soup.find('div', id='js_content')
    if content_area:
        # 提取文本
        for section in content_area.find_all(['section', 'p'], recursive=False):  # 遍历顶级section
            text = section.get_text(separator=' ', strip=True)
            if text and text not in texts:
                texts.append(text)

        for img in content_area.find_all('img', class_='rich_pages wxw-img'):
            img_src = img.get('data-src') or img.get('src')
            if img_src:
                images.add(img_src)
        cleaned_texts = [t for t in texts if t.strip()]
        content = '\n'.join(cleaned_texts)
    else:
        logger.warning(f"failed to analysis contents {url}")
        return 0, {}
    if content:
        content = f"({profile_nickname} 文章){content}"
    else:
        # If the content does not have it, but the summary has it, it means that it is an mp of the picture sharing type.
        # At this time, you can use the summary as the content.
        content = f"({profile_nickname} 文章){summary}"

    # Get links to images in meta property = "og: image" and meta property = "twitter: image"
    og_image = soup.find('meta', property='og:image')
    twitter_image = soup.find('meta', property='twitter:image')
    if og_image:
        images.add(og_image['content'])
    if twitter_image:
        images.add(twitter_image['content'])

    if rich_media_title == summary or not summary:
        abstract = ''
    else:
        abstract = f"({profile_nickname} 文章){rich_media_title}——{summary}"

    return 11, {
        'title': rich_media_title,
        'author': profile_nickname,
        'publish_time': publish_time,
        'abstract': abstract,
        'content': content,
        'images': list(images),
        'url': url,
    }
