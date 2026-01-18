#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单更新脚本 - 教师文档管理系统
使用方法: python 简单更新.py 新版本.zip
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime

def print_step(step, message):
    """打印步骤信息"""
    print(f"[步骤 {step}] {message}")

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")

def print_warning(message):
    """打印警告信息"""
    print(f"⚠️  {message}")

def create_backup():
    """创建备份"""
    print_step(1, "创建系统备份...")
    
    try:
        # 创建备份目录
        backup_dir = os.path.join(os.getcwd(), 'media', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份名称
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_更新前_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # 备份用户文件
        user_files_path = os.path.join(os.getcwd(), 'media', 'user_files')
        if os.path.exists(user_files_path):
            shutil.copytree(user_files_path, os.path.join(backup_path, 'user_files'))
            print_success("用户文件备份完成")
        
        # 备份配置文件
        env_file = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file):
            os.makedirs(backup_path, exist_ok=True)
            shutil.copy2(env_file, os.path.join(backup_path, '.env'))
            print_success("配置文件备份完成")
        
        print_success(f"备份创建完成: {backup_path}")
        return True
        
    except Exception as e:
        print_error(f"备份失败: {str(e)}")
        return False

def update_from_zip(zip_path):
    """从zip文件更新"""
    print_step(2, f"从 {zip_path} 更新系统...")
    
    try:
        # 创建临时目录
        temp_dir = os.path.join(os.getcwd(), 'temp_update')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        # 解压文件
        print("正在解压文件...")
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
            print_error("未找到项目目录")
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
                print(f"  📁 更新目录: {dir_name}")
        
        # 更新文件
        for file_name in update_files:
            src_path = os.path.join(project_dir, file_name)
            dst_path = os.path.join(os.getcwd(), file_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                shutil.copy2(src_path, dst_path)
                print(f"  📄 更新文件: {file_name}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        print_success("文件更新完成")
        return True
        
    except Exception as e:
        print_error(f"更新失败: {str(e)}")
        return False

def run_migrations():
    """运行数据库迁移"""
    print_step(3, "运行数据库迁移...")
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("数据库迁移完成")
            return True
        else:
            print_warning(f"数据库迁移失败: {result.stderr}")
            return False
            
    except Exception as e:
        print_warning(f"数据库迁移失败: {str(e)}")
        return False

def collect_static():
    """收集静态文件"""
    print_step(4, "收集静态文件...")
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("静态文件收集完成")
            return True
        else:
            print_warning(f"静态文件收集失败: {result.stderr}")
            return False
            
    except Exception as e:
        print_warning(f"静态文件收集失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("教师文档管理系统 - 简单更新工具")
    print("=" * 60)
    print()
    
    if len(sys.argv) != 2:
        print("❌ 使用方法: python 简单更新.py <新版本zip文件路径>")
        print()
        print("📋 使用步骤:")
        print("  1. 将新版本zip文件放在项目根目录")
        print("  2. 运行: python 简单更新.py 新版本.zip")
        print("  3. 等待更新完成")
        print("  4. 启动服务器: python start_lan.py")
        print()
        return
    
    zip_path = sys.argv[1]
    
    if not os.path.exists(zip_path):
        print_error(f"文件不存在: {zip_path}")
        print()
        print("请确认:")
        print("  1. 文件路径是否正确")
        print("  2. 文件是否存在于当前目录")
        print("  3. 文件名是否正确（包括扩展名）")
        return
    
    print(f"✅ 找到更新文件: {zip_path}")
    print()
    
    # 执行更新流程
    success = True
    
    # 1. 创建备份
    if not create_backup():
        print_warning("备份失败，但继续更新...")
    
    # 2. 更新文件
    if not update_from_zip(zip_path):
        print_error("文件更新失败")
        success = False
    
    # 3. 运行迁移
    if not run_migrations():
        print_warning("数据库迁移失败，请手动运行: python manage.py migrate")
    
    # 4. 收集静态文件
    if not collect_static():
        print_warning("静态文件收集失败，请手动运行: python manage.py collectstatic")
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ 系统更新成功完成！")
        print()
        print("🚀 下一步操作:")
        print("  1. 启动服务器: python start_lan.py")
        print("  2. 访问系统: http://localhost:8000")
        print("  3. 检查功能是否正常")
        print()
        print("💾 备份位置: media/backups/")
    else:
        print("❌ 系统更新失败！")
        print()
        print("🔧 故障排除:")
        print("  1. 检查Python环境是否正确")
        print("  2. 确认zip文件格式正确")
        print("  3. 查看错误信息并手动处理")
        print("  4. 如需恢复，请从备份目录恢复")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
