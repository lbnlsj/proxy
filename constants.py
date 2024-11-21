from enum import Enum, auto


class ProxyProtocol(Enum):
    HTTP = auto()
    HTTPS = auto()
    SOCKS4 = auto()
    SOCKS5 = auto()


class ProxyError(Exception):
    """自定义代理异常基类"""
    pass


class ProxyConfigError(ProxyError):
    """代理配置错误"""
    pass


class ProxyConnectionError(ProxyError):
    """代理连接错误"""
    pass


# Windows API 常量
INTERNET_OPTION_REFRESH = 37
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_PER_CONNECTION_OPTION = 75
INTERNET_PER_CONN_FLAGS = 1
INTERNET_PER_CONN_PROXY_SERVER = 2
INTERNET_PER_CONN_PROXY_BYPASS = 3
PROXY_TYPE_DIRECT = 1
PROXY_TYPE_PROXY = 2
