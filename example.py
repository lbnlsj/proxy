import threading
import time
import logging
from typing import List, Optional
import requests
from proxy_controller import WindowsProxyController
from proxy_tester import ProxyTester
from constants import ProxyError


class ProxyTestWorker:
    """代理测试工作类"""

    def __init__(self, proxy: str, test_urls: Optional[List[str]] = None):
        self.proxy = proxy
        self.test_urls = test_urls or [
            'http://example.com',
            'https://httpbin.org/ip',
            'https://api.ipify.org?format=json'
        ]
        self.results = {
            'success': False,
            'external_ip': None,
            'response_times': [],
            'errors': []
        }

    def test_connection(self, controller: WindowsProxyController) -> bool:
        """测试代理连接"""
        try:
            session = requests.Session()
            for url in self.test_urls:
                start_time = time.time()
                response = session.get(url, timeout=10)
                elapsed = time.time() - start_time

                self.results['response_times'].append({
                    'url': url,
                    'time': elapsed
                })

                if response.status_code != 200:
                    self.results['errors'].append(
                        f"Status code {response.status_code} for {url}"
                    )
                    return False
            return True
        except Exception as e:
            self.results['errors'].append(str(e))
            return False

    def check_ip(self, session: requests.Session) -> Optional[str]:
        """检查当前使用的IP地址"""
        try:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            return response.json().get('ip')
        except Exception as e:
            self.results['errors'].append(f"IP check failed: {str(e)}")
            return None


def worker_thread(controller: WindowsProxyController,
                  tester: ProxyTester,
                  proxy: str,
                  test_name: str = ""):
    """工作线程函数"""
    thread_id = threading.get_ident()
    logger = logging.getLogger(f'ProxyTest.{test_name or thread_id}')

    logger.info(f"Starting proxy test for {proxy}")
    worker = ProxyTestWorker(proxy)

    try:
        # 设置代理
        if not controller.set_thread_proxy(proxy, validate=True):
            logger.error(f"Failed to set proxy {proxy}")
            return

        logger.info(f"Successfully set proxy {proxy}")

        # 测试连接
        if worker.test_connection(controller):
            logger.info(f"Connection test passed for {proxy}")

            # 获取外部IP
            external_ip = tester.get_external_ip(proxy)
            if external_ip:
                logger.info(f"External IP: {external_ip}")
                worker.results['external_ip'] = external_ip
                worker.results['success'] = True
            else:
                logger.warning("Could not determine external IP")
        else:
            logger.error(f"Connection test failed for {proxy}")

        # 性能测试
        if worker.results['response_times']:
            avg_time = sum(r['time'] for r in worker.results['response_times']) / len(worker.results['response_times'])
            logger.info(f"Average response time: {avg_time:.2f} seconds")

    except ProxyError as e:
        logger.error(f"Proxy error: {str(e)}")
        worker.results['errors'].append(str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        worker.results['errors'].append(str(e))
    finally:
        # 清理代理设置
        if not controller.disable_thread_proxy():
            logger.warning("Failed to disable proxy")
        else:
            logger.info("Successfully disabled proxy")

        # 输出最终结果
        result_str = "SUCCESS" if worker.results['success'] else "FAILED"
        logger.info(f"Test completed - Status: {result_str}")
        if worker.results['errors']:
            logger.info("Errors encountered:")
            for error in worker.results['errors']:
                logger.info(f"  - {error}")


def run_proxy_tests(proxies: List[str], concurrent: bool = True):
    """运行代理测试"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('ProxyTest')

    # 创建控制器和测试器
    controller = WindowsProxyController()
    tester = ProxyTester(controller)

    logger.info(f"Starting proxy tests for {len(proxies)} proxies")
    logger.info(f"Mode: {'Concurrent' if concurrent else 'Sequential'}")

    if concurrent:
        # 并发测试
        threads = []
        for i, proxy in enumerate(proxies, 1):
            thread = threading.Thread(
                target=worker_thread,
                args=(controller, tester, proxy, f"Test{i}"),
                name=f"ProxyTest{i}"
            )
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()
    else:
        # 顺序测试
        for i, proxy in enumerate(proxies, 1):
            logger.info(f"Running test {i}/{len(proxies)}")
            worker_thread(controller, tester, proxy, f"Test{i}")

    logger.info("All proxy tests completed")


def main():
    """主函数"""
    # 测试代理列表
    test_proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080",
        "http://proxy4.example.com:3128"
    ]

    # 运行测试示例

    # 1. 并发测试所有代理
    print("\n=== Running concurrent tests ===")
    run_proxy_tests(test_proxies, concurrent=True)

    # 2. 顺序测试所有代理
    print("\n=== Running sequential tests ===")
    run_proxy_tests(test_proxies, concurrent=False)

    # 3. 单个代理测试示例
    print("\n=== Running single proxy test ===")
    controller = WindowsProxyController()
    tester = ProxyTester(controller)

    single_proxy = "http://proxy1.example.com:8080"
    worker_thread(controller, tester, single_proxy, "SingleTest")


if __name__ == "__main__":
    main()