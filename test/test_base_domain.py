import unittest
import os
import sys

# 将core目录添加到Python路径
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(core_path)
from core.wwd.utils import get_base_domain, is_external_url

class TestURLUtils(unittest.TestCase):
    def test_get_base_domain(self):
        # Test cases for get_base_domain
        test_cases = [
            # Basic URLs
            ("https://example.com", "example.com"),
            ("http://www.example.com", "example.com"),
            ("https://sub.example.com", "example.com"),
            
            # URLs with ports
            ("https://example.com:8080", "example.com"),
            ("http://www.example.com:443", "example.com"),
            
            # Special TLDs
            ("https://example.co.uk", "example.co.uk"),
            ("http://www.example.org.uk", "example.org.uk"),
            ("https://example.ac.jp", "example.ac.jp"),
            
            # Complex domains
            ("https://sub.sub.example.com", "example.com"),
            ("http://www.sub.example.co.uk", "example.co.uk"),
            
            # Edge cases
            ("", ""),
            ("not-a-url", ""),
            ("https://", ""),
            ("http://localhost", "localhost"),
            ("https://127.0.0.1", "127.0.0.1"),
            
            # URLs with paths
            ("https://example.com/path", "example.com"),
            ("http://www.example.com/path/to/page", "example.com"),
            
            # URLs with query parameters
            ("https://example.com?param=value", "example.com"),
            ("http://www.example.com/path?param=value", "example.com"),
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = get_base_domain(url)
                self.assertEqual(result, expected, f"Failed for URL: {url}")

    def test_is_external_url(self):
        # Test cases for is_external_url
        base_url = "https://example.com"
        
        test_cases = [
            # Internal URLs
            ("https://example.com/page", False),
            ("http://www.example.com/page", False),
            ("https://sub.example.com/page", False),
            ("/relative/path", False),
            ("relative/path", False),
            
            # External URLs
            ("https://other.com", True),
            ("http://www.other.com", True),
            ("https://example.org", True),
            ("https://example.co.uk", True),
            
            # Edge cases
            ("", False),
            ("not-a-url", False),
            ("https://", False),
            ("http://localhost", True),
            ("https://127.0.0.1", True),
            
            # URLs with ports
            ("https://example.com:8080", False),
            ("https://other.com:8080", True),
            
            # Complex domains
            ("https://sub.sub.example.com", False),
            ("https://sub.sub.other.com", True),
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = is_external_url(url, base_url)
                self.assertEqual(result, expected, f"Failed for URL: {url}")

    def test_is_external_url_with_different_base_urls(self):
        # Test is_external_url with different base URLs
        test_cases = [
            # Base URL: example.co.uk
            ("example.co.uk", "https://example.co.uk/page", False),
            ("example.co.uk", "https://sub.example.co.uk/page", False),
            ("example.co.uk", "https://other.co.uk/page", True),
            
            # Base URL: example.ac.jp
            ("example.ac.jp", "https://example.ac.jp/page", False),
            ("example.ac.jp", "https://sub.example.ac.jp/page", False),
            ("example.ac.jp", "https://other.ac.jp/page", True),
            
            # Base URL: localhost
            ("localhost", "http://localhost/page", False),
            ("localhost", "http://127.0.0.1/page", True),
            
            # Base URL: IP address
            ("127.0.0.1", "http://127.0.0.1/page", False),
            ("127.0.0.1", "http://localhost/page", True),
        ]
        
        for base_domain, url, expected in test_cases:
            with self.subTest(base_domain=base_domain, url=url):
                result = is_external_url(url, f"https://{base_domain}")
                self.assertEqual(result, expected, 
                               f"Failed for base domain: {base_domain}, URL: {url}")

if __name__ == '__main__':
    # unittest.main() 
    test_list = ['https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIxMzkyNjE5OQ==&action=getalbum&album_id=3313733712991387654',
                 'https://mp.weixin.qq.com/s?__biz=MzAxMjc3MjkyMg==&mid=2648392066&idx=1&sn=c46a35c0158fb83ea69405dc87806c87',
                 ]
    for url in test_list:
        print(get_base_domain(url))
        print(is_external_url(url, 'https://mp.weixin.qq.com'))
