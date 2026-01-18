#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速更新脚本 - 用于更新教师文档管理系统
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_backup():
    """创建快速备份"""
    log("创建系统备份...")
    
    try:
        # 创建备份目录
        backup_dir = os.path.join(os.getcwd(), 'media', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份媒体文件
        media_backup = os.path.join(backup_dir, f"media_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        user_files_path = os.path.join(os.getcwd(), 'media', 'user_files')
        
        if os.path.exists(user_files_path):
            shutil.copytree(user_files_path, media_backup)
            log(f"媒体文件备份完成: {media_backup}")
        
        # 备份配置文件
        env_file = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file):
            shutil.copy2(env_file, os.path.join(backup_dir, f"env_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"))
            log("配置文件备份完成")
        
        return True
        
    except Exception as e:
        log(f"备份失败: {str(e)}")
        return False

def update_from_zip(zip_path):
    """从zip文件更新系统"""
    log(f"开始从 {zip_path} 更新系统...")
    
    try:
        # 创建临时目录
        temp_dir = os.path.join(os.getcwd(), 'temp_update')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 找到项目目录
        project_dir = None
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and 'teacher_doc_system' in item:
                project_dir = item_path
                break
        
        if not project_dir:
            log("未找到项目目录")
            return False
        
        # 需要保留的文件和目录
        preserve_items = [
            'media/user_files',
            'media/backups', 
            'logs',
            '.env'
        ]
        
        # 需要更新的目录
        update_dirs = [
            'templates',
            'static', 
            'users',
            'documents',
            'system',
            'accounts',
            'teacher_doc_system'
        ]
        
        # 需要更新的文件
        update_files = [
            'manage.py',
            'requirements.txt',
            'start_lan.bat',
            'start_local.bat', 
            'start.py',
            'stop.bat',
            'stop.py'
        ]
        
        # 更新目录
        for dir_name in update_dirs:
            src_path = os.path.join(project_dir, dir_name)
            dst_path = os.path.join(os.getcwd(), dir_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                log(f"更新目录: {dir_name}")
        
        # 更新文件
        for file_name in update_files:
            src_path = os.path.join(project_dir, file_name)
            dst_path = os.path.join(os.getcwd(), file_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                shutil.copy2(src_path, dst_path)
                log(f"更新文件: {file_name}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        log("文件更新完成")
        return True
        
    except Exception as e:
        log(f"更新失败: {str(e)}")
        return False

def run_migrations():
    """运行数据库迁移"""
    log("运行数据库迁移...")
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            log("数据库迁移完成")
            return True
        else:
            log(f"数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"数据库迁移失败: {str(e)}")
        return False

def collect_static():
    """收集静态文件"""
    log("收集静态文件...")
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            log("静态文件收集完成")
            return True
        else:
            log(f"静态文件收集失败: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"静态文件收集失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("教师文档管理系统 - 快速更新工具")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("使用方法: python quick_update.py <新版本zip文件路径>")
        print("示例: python quick_update.py new_version.zip")
        return
    
    zip_path = sys.argv[1]
    
    if not os.path.exists(zip_path):
        print(f"错误: 文件不存在 - {zip_path}")
        return
    
    # 确认更新
    print(f"准备更新系统，新版本文件: {zip_path}")
    print("注意: 此操作将更新系统代码，但会保留用户数据")
    confirm = input("确认继续更新吗？(y/N): ")
    
    if confirm.lower() != 'y':
        print("更新已取消")
        return
    
    # 执行更新流程
    log("开始更新流程...")
    
    # 1. 创建备份
    if not create_backup():
        log("备份失败，但继续更新...")
    
    # 2. 更新文件
    if not update_from_zip(zip_path):
        log("文件更新失败")
        return
    
    # 3. 运行迁移
    if not run_migrations():
        log("数据库迁移失败，请手动运行: python manage.py migrate")
    
    # 4. 收集静态文件
    if not collect_static():
        log("静态文件收集失败，请手动运行: python manage.py collectstatic")
    
    print("\n" + "=" * 50)
    print("✅ 系统更新完成！")
    print("下一步:")
    print("1. 重启服务器: python start_lan.py")
    print("2. 检查系统功能")
    print("3. 如有问题，可从 media/backups/ 恢复")
    print("=" * 50)

if __name__ == "__main__":
    main()
