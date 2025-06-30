# Utility functions for simplified engines
from __future__ import annotations
from lxml import html
import random
from typing import Optional
from numbers import Number
from html.parser import HTMLParser
from html import escape

from lxml import html
from lxml.etree import ElementBase, XPath, XPathError, XPathSyntaxError


class _NotSetClass:  # pylint: disable=too-few-public-methods
    pass
_NOTSET = _NotSetClass()

def get_xpath(xpath_spec) -> XPath:
    if isinstance(xpath_spec, str):
        return XPath(xpath_spec)
    if isinstance(xpath_spec, XPath):
        return xpath_spec

def eval_xpath(element: ElementBase, xpath_spec):
    xpath = get_xpath(xpath_spec)
    try:
        return xpath(element)
    except XPathError as e:
        arg = ' '.join([str(i) for i in e.args])
        raise ValueError(f"Error evaluating XPath: '{xpath_spec}'. Original error: {arg}") from e

def eval_xpath_list(element: ElementBase, xpath_spec, min_len: Optional[int] = None):
    result = eval_xpath(element, xpath_spec)
    if not isinstance(result, list):
        raise ValueError(f"the result is not a list: {result}")
    if min_len is not None and min_len > len(result):
        raise ValueError(f"len(xpath_str) < {min_len}")
    return result

def eval_xpath_getindex(elements: ElementBase, xpath_spec, index: int, default=_NOTSET):
    result = eval_xpath_list(elements, xpath_spec)
    if -len(result) <= index < len(result):
        return result[index]
    if default == _NOTSET:
        raise ValueError(f"index {index} not found")
    return default

# HTML processing utilities (copied and adapted from searx/utils.py)
_BLOCKED_TAGS = ('script', 'style')

class _HTMLTextExtractorException(Exception):
    pass

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == 'br':
            self.result.append(' ')

    def handle_endtag(self, tag):
        if not self.tags:
            return
        if tag != self.tags[-1]:
            raise _HTMLTextExtractorException()
        self.tags.pop()

    def is_valid_tag(self):
        return not self.tags or self.tags[-1] not in _BLOCKED_TAGS

    def handle_data(self, data):
        if not self.is_valid_tag():
            return
        self.result.append(data)

    def handle_charref(self, name):
        if not self.is_valid_tag():
            return
        if name[0] in ('x', 'X'):
            codepoint = int(name[1:], 16)
        else:
            codepoint = int(name)
        self.result.append(chr(codepoint))

    def handle_entityref(self, name):
        if not self.is_valid_tag():
            return
        self.result.append(name) # Simplified from original, might need html.entities.name2codepoint

    def get_text(self):
        return ''.join(self.result).strip()

    def error(self, message):
        raise AssertionError(message)

def html_to_text(html_str: str) -> str:
    if not html_str:
        return ""
    html_str = html_str.replace('\n', ' ').replace('\r', ' ')
    html_str = ' '.join(html_str.split())
    s = _HTMLTextExtractor()
    try:
        s.feed(html_str)
    except AssertionError: # Error during parsing
        s = _HTMLTextExtractor()
        s.feed(escape(html_str, quote=True)) # Try with escaped string
    except _HTMLTextExtractorException: # Custom internal error
        # Potentially log this in a real scenario
        pass # Keep it simple for now
    return s.get_text()

def extract_text(xpath_results, allow_none: bool = False) -> Optional[str]:
    if isinstance(xpath_results, list):
        result = ''
        for e in xpath_results:
            result = result + (extract_text(e) or '')
        return result.strip()
    if isinstance(xpath_results, ElementBase):
        text: str = html.tostring(xpath_results, encoding='unicode', method='text', with_tail=False)
        text = text.strip().replace('\n', ' ')
        return ' '.join(text.split())
    if isinstance(xpath_results, (str, Number, bool)):
        return str(xpath_results)
    if xpath_results is None and allow_none:
        return None
    if xpath_results is None and not allow_none:
        raise ValueError('extract_text(None, allow_none=False)')
    raise ValueError(f'unsupported type: {type(xpath_results)}')

def gen_useragent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    return random.choice(user_agents)
