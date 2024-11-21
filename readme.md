# Windows 线程级代理控制器

## 目录
- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [安装说明](#安装说明)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [代码结构](#代码结构)
- [示例代码](#示例代码)
- [常见问题](#常见问题)
- [注意事项](#注意事项)

## 项目简介

Windows 线程级代理控制器是一个用于在 Windows 系统上实现线程级别代理控制的 Python 工具包。它允许不同的线程使用不同的代理设置，支持多种代理协议，并提供了完整的代理验证和测试功能。

### 主要特点
- 支持线程级别的代理控制
- 支持多种代理协议（HTTP/HTTPS/SOCKS4/SOCKS5）
- 提供代理验证和测试功能
- 集成日志系统
- 支持代理自动测试和 IP 检测

## 功能特性

### 核心功能
1. **线程级代理控制**
   - 为不同线程设置不同的代理
   - 动态启用/禁用代理
   - 线程安全操作

2. **代理协议支持**
   - HTTP 代理
   - HTTPS 代理
   - SOCKS4 代理
   - SOCKS5 代理

3. **代理验证功能**
   - 代理格式验证
   - 代理连接测试
   - 代理可用性检查

4. **监控和测试**
   - 外部 IP 检测
   - 代理性能测试
   - 完整的日志记录

## 安装说明

### 系统要求
- Windows 7 或更高版本
- Python 3.7 或更高版本
- 管理员权限

### 依赖安装
```bash
# 基本依赖
pip install requests

# SOCKS 代理支持（可选）
pip install requests[socks]
```

### 项目文件结构
```
proxy_controller/
├── constants.py        # 常量和枚举定义
├── win_structures.py   # Windows API 结构
├── proxy_validator.py  # 代理验证模块
├── proxy_controller.py # 核心控制器
├── proxy_tester.py     # 代理测试模块
└── example.py         # 使用示例
```

## 使用指南

### 基本使用

1. **创建控制器实例**
```python
from proxy_controller import WindowsProxyController

controller = WindowsProxyController()
```

2. **设置线程代理**
```python
# 设置 HTTP 代理
controller.set_thread_proxy("http://proxy.example.com:8080")

# 设置 SOCKS5 代理
controller.set_thread_proxy("socks5://proxy.example.com:1080")
```

3. **禁用线程代理**
```python
controller.disable_thread_proxy()
```

### 代理测试

1. **创建测试器实例**
```python
from proxy_tester import ProxyTester

tester = ProxyTester(controller)
```

2. **测试代理可用性**
```python
proxy = "http://proxy.example.com:8080"
if tester.test_proxy(proxy):
    print("代理可用")
else:
    print("代理不可用")
```

3. **检查外部 IP**
```python
external_ip = tester.get_external_ip(proxy)
print(f"当前使用的 IP: {external_ip}")
```

## API 文档

### WindowsProxyController 类

#### 方法
- `set_thread_proxy(proxy_server: str, bypass_list: str = "localhost;127.0.0.1", validate: bool = True) -> bool`
  - 设置当前线程的代理
  - 参数：
    - proxy_server: 代理服务器地址
    - bypass_list: 绕过代理的地址列表
    - validate: 是否验证代理
  - 返回：设置是否成功

- `disable_thread_proxy() -> bool`
  - 禁用当前线程的代理
  - 返回：操作是否成功

- `get_thread_proxy() -> Optional[Tuple[str, str]]`
  - 获取当前线程的代理设置
  - 返回：(代理服务器, 绕过列表) 或 None

- `list_all_proxies() -> Dict[int, Tuple[str, str]]`
  - 列出所有线程的代理设置
  - 返回：线程ID到代理设置的映射

### ProxyTester 类

#### 方法
- `test_proxy(proxy: str) -> bool`
  - 测试代理是否可用
  - 参数：
    - proxy: 代理服务器地址
  - 返回：代理是否可用

- `get_external_ip(proxy: Optional[str] = None) -> Optional[str]`
  - 获取使用代理后的外部 IP
  - 参数：
    - proxy: 可选的代理服务器地址
  - 返回：外部 IP 或 None

## 代码结构

### 模块说明

1. **constants.py**
   - 定义常量和枚举类型
   - 自定义异常类

2. **win_structures.py**
   - Windows API 相关结构定义
   - 用于与系统 API 交互

3. **proxy_validator.py**
   - 代理格式验证
   - 代理连接测试
   - 协议解析功能

4. **proxy_controller.py**
   - 核心代理控制逻辑
   - 线程管理
   - 系统设置操作

5. **proxy_tester.py**
   - 代理功能测试
   - IP 检测功能

## 示例代码

### 多线程代理使用示例
```python
import threading
from proxy_controller import WindowsProxyController
from proxy_tester import ProxyTester

def worker_thread(controller, tester, proxy):
    if controller.set_thread_proxy(proxy):
        external_ip = tester.get_external_ip()
        print(f"线程 {threading.get_ident()}: 使用代理 {proxy}")
        print(f"外部 IP: {external_ip}")
    
    # 执行需要代理的操作
    
    controller.disable_thread_proxy()

# 创建控制器和测试器
controller = WindowsProxyController()
tester = ProxyTester(controller)

# 启动多个线程
proxies = [
    "http://proxy1:8080",
    "http://proxy2:8080"
]

threads = []
for proxy in proxies:
    thread = threading.Thread(
        target=worker_thread,
        args=(controller, tester, proxy)
    )
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()
```

## 常见问题

### 1. 权限问题
**问题**：设置代理时报错 "Access Denied"
**解决**：以管理员权限运行 Python 程序

### 2. 代理无法连接
**问题**：代理设置成功但无法访问网络
**解决方案**：
- 检查代理服务器是否正常运行
- 验证代理服务器地址和端口是否正确
- 检查防火墙设置

### 3. SOCKS 代理不工作
**问题**：SOCKS 代理设置后无法使用
**解决方案**：
- 安装 SOCKS 支持：`pip install requests[socks]`
- 确保代理服务器支持对应的 SOCKS 版本

