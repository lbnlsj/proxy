import threading
import logging
from typing import Dict, Tuple, Optional
import ctypes
import win_structures
from constants import *
from proxy_validator import ProxyValidator


class WindowsProxyController:
    def __init__(self, enable_logging: bool = True):
        self._thread_proxies: Dict[int, Tuple[str, str]] = {}
        self._lock = threading.Lock()
        self._wininet = ctypes.WinDLL('wininet', use_last_error=True)
        self._validator = ProxyValidator()
        self._setup_logging(enable_logging)
        self._setup_wininet()

    def _setup_logging(self, enable_logging: bool):
        """设置日志系统"""
        self.logger = logging.getLogger('WindowsProxyController')
        if enable_logging:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _setup_wininet(self):
        """设置WinINet函数参数类型"""
        self._wininet.InternetSetOptionW.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.c_void_p,
            ctypes.wintypes.DWORD
        ]

    def _set_proxy_options(self, proxy_server: Optional[str] = None,
                           bypass_list: str = "") -> bool:
        """设置代理选项"""
        try:
            options = (win_structures.INTERNET_PER_CONN_OPTION * 3)()

            # 设置代理标志
            options[0].dwOption = INTERNET_PER_CONN_FLAGS
            options[0].Value.dwValue = (PROXY_TYPE_PROXY | PROXY_TYPE_DIRECT
                                        if proxy_server else PROXY_TYPE_DIRECT)

            # 设置代理服务器
            options[1].dwOption = INTERNET_PER_CONN_PROXY_SERVER
            options[1].Value.pszValue = (ctypes.create_unicode_buffer(proxy_server)
                                         if proxy_server else None)

            # 设置绕过列表
            options[2].dwOption = INTERNET_PER_CONN_PROXY_BYPASS
            options[2].Value.pszValue = ctypes.create_unicode_buffer(bypass_list)

            # 创建选项列表结构
            option_list = win_structures.INTERNET_PER_CONN_OPTION_LIST()
            option_list.dwSize = ctypes.sizeof(
                win_structures.INTERNET_PER_CONN_OPTION_LIST
            )
            option_list.pszConnection = None
            option_list.dwOptionCount = 3
            option_list.dwOptionError = 0
            option_list.pOptions = options

            # 应用设置
            size = ctypes.sizeof(option_list)
            result = self._wininet.InternetSetOptionW(
                None,
                INTERNET_OPTION_PER_CONNECTION_OPTION,
                ctypes.byref(option_list),
                size
            )

            if result:
                # 刷新设置
                self._wininet.InternetSetOptionW(
                    None, INTERNET_OPTION_SETTINGS_CHANGED, None, 0
                )
                self._wininet.InternetSetOptionW(
                    None, INTERNET_OPTION_REFRESH, None, 0
                )
                return True

            error = ctypes.get_last_error()
            self.logger.error(f"Failed to set proxy options. Error code: {error}")
            return False

        except Exception as e:
            self.logger.error(f"Error setting proxy options: {str(e)}")
            return False

    def set_thread_proxy(self, proxy_server: str,
                         bypass_list: str = "localhost;127.0.0.1",
                         validate: bool = True) -> bool:
        """为当前线程设置代理"""
        thread_id = threading.get_ident()

        try:
            # 验证代理格式
            if validate:
                if not self._validator.validate_proxy_format(proxy_server):
                    raise ProxyConfigError("Invalid proxy format")

                if not self._validator.validate_proxy_connection(proxy_server):
                    raise ProxyConnectionError("Cannot connect to proxy server")

            with self._lock:
                if self._set_proxy_options(proxy_server, bypass_list):
                    self._thread_proxies[thread_id] = (proxy_server, bypass_list)
                    self.logger.info(
                        f"Thread {thread_id}: Proxy set to {proxy_server}"
                    )
                    return True

                self.logger.error(
                    f"Thread {thread_id}: Failed to set proxy {proxy_server}"
                )
                return False

        except ProxyError as e:
            self.logger.error(f"Thread {thread_id}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Thread {thread_id}: Unexpected error: {str(e)}")
            return False

    def disable_thread_proxy(self) -> bool:
        """禁用当前线程的代理"""
        thread_id = threading.get_ident()

        try:
            with self._lock:
                if thread_id in self._thread_proxies:
                    if self._set_proxy_options(None):
                        del self._thread_proxies[thread_id]
                        self.logger.info(f"Thread {thread_id}: Proxy disabled")
                        return True

                    self.logger.error(
                        f"Thread {thread_id}: Failed to disable proxy"
                    )
                    return False

                self.logger.warning(
                    f"Thread {thread_id}: No proxy settings found"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Thread {thread_id}: Error disabling proxy: {str(e)}"
            )
            return False

    def get_thread_proxy(self) -> Optional[Tuple[str, str]]:
        """获取当前线程的代理设置"""
        thread_id = threading.get_ident()
        with self._lock:
            return self._thread_proxies.get(thread_id)

    def list_all_proxies(self) -> Dict[int, Tuple[str, str]]:
        """列出所有线程的代理设置"""
        with self._lock:
            return self._thread_proxies.copy()


