import re
import socket
from typing import Optional
from constants import ProxyProtocol, ProxyConfigError


class ProxyValidator:
    @staticmethod
    def validate_proxy_format(proxy_server: str) -> bool:
        """验证代理服务器格式"""
        proxy_pattern = r'^(http|https|socks4|socks5)://[\w.-]+:\d+$'
        return bool(re.match(proxy_pattern, proxy_server))

    @staticmethod
    def validate_proxy_connection(proxy_server: str, timeout: int = 5) -> bool:
        """验证代理服务器连接"""
        try:
            protocol, address = proxy_server.split('://')
            host, port = address.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, int(port)))
            sock.close()
            return True
        except Exception:
            return False

    @staticmethod
    def parse_proxy_protocol(proxy_server: str) -> Optional[ProxyProtocol]:
        """解析代理协议类型"""
        protocol_map = {
            'http': ProxyProtocol.HTTP,
            'https': ProxyProtocol.HTTPS,
            'socks4': ProxyProtocol.SOCKS4,
            'socks5': ProxyProtocol.SOCKS5
        }
        try:
            protocol = proxy_server.split('://')[0].lower()
            return protocol_map.get(protocol)
        except Exception:
            return None

