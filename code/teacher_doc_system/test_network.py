#!/usr/bin/env python
"""
网络连接测试脚本
用于测试局域网访问配置
"""

import socket
import requests
import time
import threading
from urllib.parse import urljoin

def test_port_open(host, port, timeout=3):
    """测试端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_http_response(url, timeout=5):
    """测试HTTP响应"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝"
    except requests.exceptions.Timeout:
        return False, "连接超时"
    except Exception as e:
        return False, str(e)

def get_local_ips():
    """获取所有本地IP地址"""
    ips = []
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):
                        ips.append(ip)
    except ImportError:
        # 简单方法获取IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.append(s.getsockname()[0])
            s.close()
        except:
            ips.append("127.0.0.1")
    return ips

def test_network_access():
    """测试网络访问"""
    print("=" * 60)
    print("🌐 网络连接测试")
    print("=" * 60)
    
    # 获取本地IP地址
    local_ips = get_local_ips()
    print(f"📡 检测到的IP地址: {', '.join(local_ips)}")
    print()
    
    # 测试端口
    port = 8000
    print(f"🔍 测试端口 {port} 是否开放...")
    
    for ip in local_ips:
        if test_port_open(ip, port):
            print(f"✅ {ip}:{port} - 端口开放")
            
            # 测试HTTP响应
            url = f"http://{ip}:{port}"
            print(f"🌐 测试HTTP访问: {url}")
            
            success, status = test_http_response(url)
            if success:
                print(f"✅ HTTP访问成功 (状态码: {status})")
            else:
                print(f"❌ HTTP访问失败: {status}")
        else:
            print(f"❌ {ip}:{port} - 端口未开放")
        print()
    
    # 测试localhost
    print("🏠 测试localhost访问...")
    localhost_url = f"http://localhost:{port}"
    success, status = test_http_response(localhost_url)
    if success:
        print(f"✅ localhost访问成功 (状态码: {status})")
    else:
        print(f"❌ localhost访问失败: {status}")
    
    print("=" * 60)
    print("📋 测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_network_access()
