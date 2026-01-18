#!/usr/bin/env python
"""
教师文档管理系统 - 统一启动脚本
支持本地开发和局域网访问
"""

import os
import sys
import socket
import subprocess
import platform
import argparse
from pathlib import Path

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_all_network_interfaces():
    """获取所有网络接口的IP地址"""
    interfaces = []
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):
                        interfaces.append({
                            'interface': interface,
                            'ip': ip,
                            'netmask': addr.get('netmask', 'Unknown')
                        })
    except ImportError:
        interfaces.append({'interface': 'default', 'ip': get_local_ip(), 'netmask': 'Unknown'})
    return interfaces

def check_port_available(port=8000):
    """检查端口是否可用"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.close()
        return True
    except OSError:
        return False

def setup_firewall_rule(port=8000):
    """设置Windows防火墙规则"""
    if platform.system() == "Windows":
        try:
            # 添加防火墙规则
            cmd = f'netsh advfirewall firewall add rule name="Django Dev Server" dir=in action=allow protocol=TCP localport={port}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ 已添加防火墙规则，允许端口 {port}")
            else:
                print(f"⚠️  防火墙规则添加失败: {result.stderr}")
        except Exception as e:
            print(f"⚠️  防火墙设置失败: {e}")

def start_local():
    """启动本地开发服务器"""
    print("=" * 60)
    print("🏠 教师文档管理系统 - 本地开发模式")
    print("=" * 60)
    
    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teacher_doc_system.settings')
    os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1'
    
    print("🚀 正在启动本地开发服务器...")
    print("📍 访问地址: http://localhost:8000")
    print("👤 管理员账号: admin")
    print("🔑 管理员密码: admin123456")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def start_lan():
    """启动局域网服务器"""
    print("=" * 60)
    print("🌐 教师文档管理系统 - 局域网访问模式")
    print("=" * 60)
    
    # 检查端口是否可用
    if not check_port_available(8000):
        print("❌ 端口8000已被占用，请检查是否有其他服务在运行")
        print("可以使用以下命令查看端口占用：")
        if platform.system() == "Windows":
            print("netstat -ano | findstr :8000")
        else:
            print("lsof -i :8000")
        return
    
    # 获取本机IP地址
    local_ip = get_local_ip()
    
    print(f"🖥️  本机IP地址: {local_ip}")
    print(f"🌐 局域网访问地址: http://{local_ip}:8000")
    print(f"🏠 本机访问地址: http://localhost:8000")
    print("=" * 60)
    
    # 显示所有网络接口
    interfaces = get_all_network_interfaces()
    if len(interfaces) > 1:
        print("📡 检测到的网络接口：")
        for i, interface in enumerate(interfaces, 1):
            print(f"   {i}. {interface['interface']}: {interface['ip']}")
        print("=" * 60)
    
    # 设置防火墙规则
    setup_firewall_rule(8000)
    
    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teacher_doc_system.settings')
    os.environ['ALLOWED_HOSTS'] = '*'
    
    print("🚀 正在启动Django开发服务器...")
    print("📝 管理员账号: admin")
    print("🔑 管理员密码: admin123456")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装Django: pip install django")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='教师文档管理系统启动脚本')
    parser.add_argument('--mode', choices=['local', 'lan'], default='local',
                       help='启动模式: local(本地) 或 lan(局域网)')
    
    args = parser.parse_args()
    
    if args.mode == 'local':
        start_local()
    else:
        start_lan()

if __name__ == '__main__':
    main()
