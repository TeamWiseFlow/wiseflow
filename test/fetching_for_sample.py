# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import json
import asyncio
from urllib.parse import urlparse, urljoin
import hashlib
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext, PlaywrightPreNavigationContext
from datetime import timedelta


sites = ["https://www.gd121.cn/zx/qxzx/list.shtml",
]

os.environ['CRAWLEE_STORAGE_DIR'] = 'webpage_samples/crawlee_storage'
save_dir = 'webpage_samples'

async def main(sites: list):
    crawler = PlaywrightCrawler(
        # Limit the crawl to max requests. Remove or increase it for crawling all links.
        # max_requests_per_crawl=1,
        max_request_retries=1,
        request_handler_timeout=timedelta(minutes=5)
    )

    @crawler.pre_navigation_hook
    async def log_navigation_url(context: PlaywrightPreNavigationContext) -> None:
        context.log.info(f'navigating {context.request.url} ...')

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        await context.page.wait_for_load_state('networkidle')
        await context.page.wait_for_timeout(2000)

        # Handle dialogs (alerts, confirms, prompts)
        async def handle_dialog(dialog):
            context.log.info(f'Closing dialog: {dialog.message}')
            await dialog.accept()
        context.page.on('dialog', handle_dialog)

        context.log.info('successfully finish fetching')

        folder = os.path.join(save_dir, f"{hashlib.sha256(context.request.url.encode()).hexdigest()[-6:]}")
        os.makedirs(folder, exist_ok=True)

        html = await context.page.inner_html('head')
        soup = BeautifulSoup(html, 'html.parser')
        web_title = soup.find('title')
        if web_title:
            web_title = web_title.get_text().strip()
        else:
            web_title = ''

        base_tag = soup.find('base', href=True)
        if base_tag and base_tag.get('href'):
            base_url = base_tag['href']
        else:
            # if no base tag, use the current url as base url
            parsed_url = urlparse(context.request.url)
            domain = parsed_url.netloc
            base_url = f"{parsed_url.scheme}://{domain}"

        html = await context.page.inner_html('body')

        # to use a customer scaper here

        soup = BeautifulSoup(html, 'html.parser')

        # 移除导航、页眉、页脚等通用元素
        for selector in ['div#nav', 'div.header', 'div#footer', 'nav', 'header', 'footer']:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()

        action_dict = {}
        for form in soup.find_all('form', recursive=True):
            form_dict = {}
            for input_elem in form.find_all('input'):
                input_type = input_elem.get('type', 'text')
                input_name = input_elem.get('name', f'input_{len(action_dict)}')
                input_value = ' '.join([f"{k}={v}" for k, v in input_elem.attrs.items() if k not in ['type', 'name', 'form']])
                input_dict = {
                    "type": input_type,
                    "values": [input_value] if input_value else []
                }

                # handle datalist
                if input_elem.get('list'):
                    datalist = soup.find('datalist', id=input_elem['list'])
                    if datalist:
                        options = [opt.get('value', opt.text.strip()) for opt in datalist.find_all('option')]
                        input_dict = {
                            "type": "text",
                            "values": [f"one of followings: {options}"]
                        }
                
                form_dict[input_name] = input_dict
            
            for select in form.find_all('select'):
                select_name = select.get('name', f'select_{len(form_dict)}')
                options = [opt.get('value', opt.text.strip()) for opt in select.find_all('option')]
                form_dict[select_name] = {
                    "type": "select",
                    "values": options
                }
                
            for textarea in form.find_all('textarea'):
                textarea_name = textarea.get('name', f'textarea_{len(form_dict)}')
                form_dict[textarea_name] = {
                    "type": "textarea", 
                    "values": [textarea.text.strip()]
                }
                
            if form_dict:
                form_id = form.get('id', f'form_{len(action_dict)}')
                action_dict[form_id] = form_dict
            
            form.decompose()
        
        # handle input elements that are not in any form
        for input_elem in soup.find_all('input', recursive=True):
            if input_elem.find_parent('form') is None:
                # check if the input is associated with a form by form attribute
                form_ids = input_elem.get('form', '').split()
                
                # handle input element
                input_type = input_elem.get('type', 'text')
                input_name = input_elem.get('name', f'input_{len(action_dict)}')
                input_value = ' '.join([f"{k}={v}" for k, v in input_elem.attrs.items() if k not in ['type', 'name', 'form']])
                input_dict = {
                    "type": input_type,
                    "values": [input_value] if input_value else []
                }

                # handle datalist
                if input_elem.get('list'):
                    datalist = soup.find('datalist', id=input_elem['list'])
                    if datalist:
                        options = [opt.get('value', opt.text.strip()) for opt in datalist.find_all('option')]
                        input_dict = {
                            "type": "text",
                            "values": [f"one of followings: {options}"]
                        }
                # decide the placement of the input element based on form attribute
                if form_ids:
                    for form_id in form_ids:
                        if form_id in action_dict:
                            action_dict[form_id][input_name] = input_dict
                        else:
                            action_dict[form_id] = {input_name: input_dict}
                else:
                    action_dict[input_name] = {"input": input_dict}

            input_elem.decompose()

        for button in soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'], recursive=True):
            button_name = button.get('name', '') or button.get('id', '') or button.text.strip()
            if not button_name:
                button_name = f'button_{len(action_dict)}'
            
            button_type = button.get('type', 'button')
            button_value = button.get('value', button.text.strip())
            
            action_dict[button_name] = {
                "button": {
                    "type": button_type,
                    "values": [button_value] if button_value else []
                }
            }
            
            button.decompose()

        for command in soup.find_all('command', recursive=True):
            command_name = command.get('name', '') or command.get('id', '') or command.text.strip()
            if not command_name:
                command_name = f'command_{len(action_dict)}'
            
            command_type = command.get('type', 'command')
            command_value = command.get('value', command.text.strip())
            
            action_dict[command_name] = {
                "command": {
                    "type": command_type,
                    "values": [command_value] if command_value else []
                }
            }
            
            command.decompose()

        link_dict = {}
        for img in soup.find_all('img', src=True, recursive=True):
            src = img.get('src')
            if src.startswith('#') or src.startswith('about:blank'):
                src = None
            text = img.get('alt', '').strip()
            if src:
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                key = f"url{len(link_dict)}"
                link_dict[key] = src
                text = f"{text}<img>[{key}]"

            # find all area urls related to this img
            area_urls = set()
            if img.get('usemap'):
                # remove the # at the beginning of the map name
                map_name = img.get('usemap').lstrip('#')
                # find the map tag
                map_tag = soup.find('map', {'name': map_name})
                if map_tag:
                    # get all area tags under the map
                    for area in map_tag.find_all('area', href=True):
                        area_href = area.get('href')
                        if area_href.startswith('javascript:') or area_href.startswith('#') or area_href.startswith('mailto:') or area_href.startswith('data:') or area_href.startswith('about:blank'):
                            area_href = None
                        if area_href:
                            if not area_href.startswith(('http://', 'https://')):
                                area_href = urljoin(base_url, area_href)
                            area_urls.add(area_href)
                            area.decompose()
                    # delete the whole map tag
                    map_tag.decompose()
            for area_url in area_urls:
                if area_url in [context.request.url, base_url]:
                    continue
                key = f"url{len(link_dict)}"
                link_dict[key] = area_url
                text = f"{text}[{key}]"

            img.replace_with(f"-{text}")

        for media in soup.find_all(['video', 'audio', 'source', 'embed', 'iframe', 'figure'], src=True, recursive=True):
            src = media.get('src')
            if src.startswith('javascript:') or src.startswith('#') or src.startswith('mailto:') or src.startswith('data:') or src.startswith('about:blank'):
                src = None
            text = media.get('alt', '').strip() or media.get_text().strip()
            if src:
                # convert relative path to full url
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(context.request.url, src)
                key = f"url{len(link_dict)}"
                link_dict[key] = src
                ext = os.path.splitext(src)[1].lstrip('.') or media.name
                text = f"{text}<{ext}>[{key}]"

            media.replace_with(f"-{text}")
        
        for obj in soup.find_all('object', data=True, recursive=True):
            data = obj.get('data')
            if data.startswith('javascript:') or data.startswith('#') or data.startswith('mailto:') or data.startswith('data:') or data.startswith('about:blank'):
                data = None
            text = obj.get('title', '').strip() or obj.get_text().strip()
            if data:
                # convert relative path to full url
                if not data.startswith(('http://', 'https://')):
                    data = urljoin(context.request.url, data)
                key = f"url{len(link_dict)}"
                link_dict[key] = data
                ext = os.path.splitext(data)[1].lstrip('.') or 'object'
                text = f"{text}<{ext}>[{key}]"

            obj.replace_with(f"-{text}")

        # process links at last, so that we can keep the image and media info in the link
        for a in soup.find_all('a', href=True, recursive=True):
            href = a.get('href')
            if href.startswith('javascript:') or href.startswith('#') or href.startswith('mailto:') or href.startswith('data:') or href.startswith('about:blank'):
                href = None
            if href:
                text = a.get_text().strip() or '-'
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(context.request.url, href)
                if href in [context.request.url, base_url]:
                    continue
                key = f"url{len(link_dict)}"
                link_dict[key] = href
                a.replace_with(f"{text}[{key}]")

        # handle headings
        for i in range(1, 7):  # h1 到 h6
            for heading in soup.find_all(f'h{i}', recursive=False):
                text = heading.get_text().strip()
                heading.replace_with(f"{'#' * i} {text}\n")

        # replace all <br> and <br/> tags with newlines
        for br in soup.find_all(['br', 'br/', 'br /', 'hr', 'hr/', 'hr /', 'wbr'], recursive=True):
            br.replace_with('\n')
        
        # handle lists
        for list_tag in soup.find_all(['ul', 'ol'], recursive=True):
            list_text = []
            for idx, item in enumerate(list_tag.find_all('li')):
                list_text.append(f"{idx + 1}. {item.get_text().strip()}")
            list_text = '\t'.join(list_text)
            list_tag.replace_with(f"{list_text}\n")

        # handle spans - merge span text with surrounding text
        for span in soup.find_all('span', recursive=True):
            span.replace_with(span.get_text().strip())
        
        # handle strikethrough text
        for del_tag in soup.find_all(['del', 's'], recursive=True):
            del_text = del_tag.get_text().strip()
            if del_text:
                del_tag.replace_with(f"{del_text}(maybe_outdated)")
            else:
                del_tag.decompose()
        
        # handle tables
        for table in soup.find_all('table', recursive=True):
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
        
        html_text = soup.get_text(strip=False, separator='\n')

        with open(os.path.join(folder, 'text.txt'), 'w') as f:
            f.write(html_text)

        with open(os.path.join(folder, 'link_dict.json'), 'w', encoding='utf-8') as f:
            json.dump(link_dict, f, indent=4, ensure_ascii=False)
        
        with open(os.path.join(folder, 'action_dict.json'), 'w', encoding='utf-8') as f:
            json.dump(action_dict, f, indent=4, ensure_ascii=False)

        # screenshot_file = os.path.join(folder, 'screenshot.jpg')
        # await context.page.screenshot(path=screenshot_file, full_page=True)

    await crawler.run(sites)

if __name__ == '__main__':
    asyncio.run(main(sites))
