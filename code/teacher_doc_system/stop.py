#!/usr/bin/env python
"""
教师文档管理系统 - 统一停止脚本
停止所有相关服务并清理资源
"""

import os
import sys
import subprocess
import platform
import argparse
import time

def run_command(command, description=""):
    """运行系统命令"""
    try:
        if description:
            print(f"🔄 {description}...")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print(f"✅ {description}成功")
                if result.stdout.strip():
                    print(f"   输出: {result.stdout.strip()}")
            return True, result.stdout, result.stderr
        else:
            print(f"⚠️  {description}完成 (可能没有相关进程)")
            return False, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ {description}失败: {e}")
        return False, "", str(e)

def stop_django_server():
    """停止Django服务器"""
    print("🛑 停止Django服务器...")
    
    if platform.system() == "Windows":
        # Windows: 查找并停止占用8000端口的进程
        success, stdout, stderr = run_command("netstat -ano | findstr :8000", "检查端口8000占用")
        if success and stdout.strip():
            print("📡 发现占用端口8000的进程:")
            for line in stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        pid = parts[-1]
                        print(f"   进程ID: {pid}")
                        run_command(f"taskkill /f /pid {pid}", f"停止进程 {pid}")
        else:
            print("✅ 端口8000未被占用")
        
        # 停止所有Python进程
        run_command("taskkill /f /im python.exe", "停止Python进程")
    else:
        # Linux/Mac: 停止相关进程
        run_command("pkill -f 'manage.py runserver'", "停止Django服务器")
        run_command("pkill -f 'python.*start'", "停止启动脚本")
        run_command("pkill -f python", "停止Python进程")

def stop_celery_services():
    """停止Celery服务"""
    print("🔄 停止Celery服务...")
    
    if platform.system() == "Windows":
        run_command("taskkill /f /im celery.exe", "停止Celery进程")
    else:
        run_command("pkill -f celery", "停止Celery进程")

def stop_redis_server():
    """停止Redis服务器"""
    print("🔴 停止Redis服务器...")
    
    if platform.system() == "Windows":
        run_command("taskkill /f /im redis-server.exe", "停止Redis进程")
    else:
        run_command("pkill -f redis-server", "停止Redis进程")

def cleanup_temp_files():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    temp_dirs = [
        'logs',
        'media/temp',
        '__pycache__',
        '*/__pycache__',
        '*/migrations/__pycache__'
    ]
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                if os.path.isdir(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
                    print(f"✅ 已清理目录: {temp_dir}")
                else:
                    os.remove(temp_dir)
                    print(f"✅ 已清理文件: {temp_dir}")
            except Exception as e:
                print(f"⚠️  清理失败 {temp_dir}: {e}")

def check_ports():
    """检查端口占用情况"""
    print("\n🔍 检查端口占用情况...")
    
    ports_to_check = [8000, 6379, 3306]
    port_names = {8000: "Django", 6379: "Redis", 3306: "MySQL"}
    
    for port in ports_to_check:
        if platform.system() == "Windows":
            success, stdout, stderr = run_command(f"netstat -ano | findstr :{port}", f"检查端口{port}")
        else:
            success, stdout, stderr = run_command(f"lsof -i :{port}", f"检查端口{port}")
        
        if success and stdout.strip():
            print(f"⚠️  端口{port} ({port_names.get(port, 'Unknown')}) 仍被占用:")
            for line in stdout.split('\n'):
                if f':{port}' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"✅ 端口{port} ({port_names.get(port, 'Unknown')}) 已释放")

def remove_firewall_rules():
    """移除防火墙规则"""
    if platform.system() == "Windows":
        print("🔥 移除防火墙规则...")
        run_command('netsh advfirewall firewall delete rule name="Django Dev Server"', "移除Django防火墙规则")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='教师文档管理系统停止脚本')
    parser.add_argument('--cleanup', action='store_true', help='清理临时文件')
    parser.add_argument('--firewall', action='store_true', help='移除防火墙规则')
    parser.add_argument('--all', action='store_true', help='停止所有服务并清理')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🛑 教师文档管理系统 - 停止所有服务")
    print("=" * 60)
    
    # 停止各种服务
    stop_django_server()
    stop_celery_services()
    stop_redis_server()
    
    # 检查端口占用
    check_ports()
    
    # 清理临时文件
    if args.cleanup or args.all:
        cleanup_temp_files()
    
    # 移除防火墙规则
    if args.firewall or args.all:
        remove_firewall_rules()
    
    print("\n" + "=" * 60)
    print("🎯 服务停止完成")
    print("=" * 60)
    
    if args.all:
        print("💡 提示: 已执行完整清理，下次启动可能需要重新设置")

if __name__ == '__main__':
    main()
