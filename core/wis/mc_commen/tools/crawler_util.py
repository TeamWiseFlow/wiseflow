# don't be evil
# for commercial use, please contact to get permission
# wiseflow opensouce do not support commercial use since 4.0


import base64
import random
import regex as re
import urllib.parse
from io import BytesIO
from typing import Dict
from PIL import Image, ImageDraw  # type: ignore


def show_qrcode(qr_code) -> None:  # type: ignore
    """parse base64 encode qrcode image and show it"""
    if "," in qr_code:
        qr_code = qr_code.split(",")[1]
    qr_code = base64.b64decode(qr_code)
    image = Image.open(BytesIO(qr_code))

    # Add a square border around the QR code and display it within the border to improve scanning accuracy.
    width, height = image.size
    new_image = Image.new('RGB', (width + 20, height + 20), color=(255, 255, 255))
    new_image.paste(image, (10, 10))
    draw = ImageDraw.Draw(new_image)
    draw.rectangle((0, 0, width + 19, height + 19), outline=(0, 0, 0), width=1)
    new_image.show()

def convert_str_cookie_to_dict(cookie_str: str) -> Dict:
    cookie_dict: Dict[str, str] = dict()
    if not cookie_str:
        return cookie_dict
    for cookie in cookie_str.split(";"):
        cookie = cookie.strip()
        if not cookie:
            continue
        cookie_list = cookie.split("=")
        if len(cookie_list) != 2:
            continue
        cookie_value = cookie_list[1]
        if isinstance(cookie_value, list):
            cookie_value = "".join(cookie_value)
        cookie_dict[cookie_list[0]] = cookie_value
    return cookie_dict


def match_interact_info_count(count_str: str) -> int:
    if not count_str:
        return 0

    match = re.search(r'\d+', count_str)
    if match:
        number = match.group()
        return int(number)
    else:
        return 0


def extract_text_from_html(html: str) -> str:
    """Extract text from HTML, removing all tags."""
    if not html:
        return ""
    # Remove script and style elements
    clean_html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    # Remove all other tags
    clean_text = re.sub(r'<[^>]+>', '', clean_html).strip()
    return clean_text


def extract_url_params_to_dict(url: str) -> Dict:
    """Extract URL parameters to dict"""
    url_params_dict = dict()
    if not url:
        return url_params_dict
    parsed_url = urllib.parse.urlparse(url)
    url_params_dict = dict(urllib.parse.parse_qsl(parsed_url.query))
    return url_params_dict
