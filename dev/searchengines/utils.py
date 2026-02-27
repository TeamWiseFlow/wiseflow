# Utility functions for simplified engines
from __future__ import annotations
from lxml import html
from random import choice
from typing import Optional
from numbers import Number
from html.parser import HTMLParser
from html import escape

from lxml import html
from lxml.etree import ElementBase, XPath, XPathError


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

class HTMLTextExtractor(HTMLParser):
    """Internal class to extract text from HTML"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.result: list[str] = []
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        if tag == 'br':
            self.result.append(' ')

    def handle_endtag(self, tag: str) -> None:
        if not self.tags:
            return

        if tag != self.tags[-1]:
            self.result.append(f"</{tag}>")
            return

        self.tags.pop()

    def is_valid_tag(self):
        return not self.tags or self.tags[-1] not in _BLOCKED_TAGS

    def handle_data(self, data: str) -> None:
        if not self.is_valid_tag():
            return
        self.result.append(data)

    def handle_charref(self, name: str) -> None:
        if not self.is_valid_tag():
            return
        if name[0] in ('x', 'X'):
            codepoint = int(name[1:], 16)
        else:
            codepoint = int(name)
        self.result.append(chr(codepoint))

    def handle_entityref(self, name: str) -> None:
        if not self.is_valid_tag():
            return
        # codepoint = htmlentitydefs.name2codepoint[name]
        # self.result.append(chr(codepoint))
        self.result.append(name)

    def get_text(self):
        return ''.join(self.result).strip()

    def error(self, message: str) -> None:
        # error handle is needed in <py3.10
        # https://github.com/python/cpython/pull/8562/files
        raise AssertionError(message)

def html_to_text(html_str: str) -> str:
    """Extract text from a HTML string

    Args:
        * html_str (str): string HTML

    Returns:
        * str: extracted text

    Examples:
        >>> html_to_text('Example <span id="42">#2</span>')
        'Example #2'

        >>> html_to_text('<style>.span { color: red; }</style><span>Example</span>')
        'Example'

        >>> html_to_text(r'regexp: (?&lt;![a-zA-Z]')
        'regexp: (?<![a-zA-Z]'

        >>> html_to_text(r'<p><b>Lorem ipsum </i>dolor sit amet</p>')
        'Lorem ipsum </i>dolor sit amet</p>'

        >>> html_to_text(r'&#x3e &#x3c &#97')
        '> < a'

    """
    if not html_str:
        return ""
    html_str = html_str.replace('\n', ' ').replace('\r', ' ')
    html_str = ' '.join(html_str.split())
    s = HTMLTextExtractor()
    try:
        s.feed(html_str)
        s.close()
    except AssertionError:
        s = HTMLTextExtractor()
        s.feed(escape(html_str, quote=True))
        s.close()
    return s.get_text()

def extract_text(
    xpath_results: list[ElementBase] | ElementBase | str | Number | bool | None,
    allow_none: bool = False,
) -> str | None:
    """Extract text from a lxml result

    * if xpath_results is list, extract the text from each result and concat the list
    * if xpath_results is a xml element, extract all the text node from it
      ( text_content() method from lxml )
    * if xpath_results is a string element, then it's already done
    """
    if isinstance(xpath_results, list):
        # it's list of result : concat everything using recursive call
        result = ''
        for e in xpath_results:
            result = result + (extract_text(e) or '')
        return result.strip()
    if isinstance(xpath_results, ElementBase):
        # it's a element
        text: str = html.tostring(  # type: ignore
            xpath_results,  # pyright: ignore[reportArgumentType]
            encoding='unicode',
            method='text',
            with_tail=False,
        )
        text = text.strip().replace('\n', ' ')  # type: ignore
        return ' '.join(text.split())  # type: ignore
    if isinstance(xpath_results, (str, Number, bool)):
        return str(xpath_results)
    if xpath_results is None and allow_none:
        return None
    if xpath_results is None and not allow_none:
        raise ValueError('extract_text(None, allow_none=False)')
    raise ValueError('unsupported type')

USER_AGENTS = {
    "os": [
        "Windows NT 10.0; Win64; x64",
        "X11; Linux x86_64"
    ],
    "ua": "Mozilla/5.0 ({os}; rv:{version}) Gecko/20100101 Firefox/{version}",
    "versions": [
        "142.0",
        "141.0"
    ]
}

def gen_useragent(os_string: str | None = None) -> str:
    """Return a random browser User Agent

    See searx/data/useragents.json
    """
    return USER_AGENTS['ua'].format(
        os=os_string or choice(USER_AGENTS['os']),
        version=choice(USER_AGENTS['versions']),
    )