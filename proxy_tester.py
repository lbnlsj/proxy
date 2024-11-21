import requests
import threading
from typing import Optional
from proxy_controller import WindowsProxyController


class ProxyTester:
    def __init__(self, controller: WindowsProxyController):
        self.controller = controller
        self.test_urls = [
            'http://example.com',
            'https://example.com',
            'http://httpbin.org/ip'
        ]

    def test_proxy(self, proxy: str) -> bool:
        """测试代理是否工作"""
        if self.controller.set_thread_proxy(proxy):
            try:
                for url in self.test_urls:
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        return False
                return True
            except Exception:
                return False
            finally:
                self.controller.disable_thread_proxy()
        return False

    def get_external_ip(self, proxy: Optional[str] = None) -> Optional[str]:
        """获取外部IP地址"""
        try:
            if proxy:
                self.controller.set_thread_proxy(proxy)

            response = requests.get('http://httpbin.org/ip')
            ip = response.json()['origin']

            if proxy:
                self.controller.disable_thread_proxy()

            return ip
        except Exception:
            return None