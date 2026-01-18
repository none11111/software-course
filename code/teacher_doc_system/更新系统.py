#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师文档管理系统 - 更新工具
使用方法: python 更新系统.py 新版本.zip
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime

def main():
    print("=" * 50)
    print("教师文档管理系统 - 更新工具")
    print("=" * 50)
    print()
    
    # 检查参数
    if len(sys.argv) != 2:
        print("使用方法: python 更新系统.py <新版本zip文件路径>")
        print()
        print("步骤:")
        print("  1. 将新版本zip文件放在项目根目录")
        print("  2. 运行: python 更新系统.py 新版本.zip")
        print("  3. 等待更新完成")
        print("  4. 启动服务器: python start_lan.py")
        print()
        input("按回车键退出...")
        return
    
    zip_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(zip_path):
        print(f"错误: 文件不存在 - {zip_path}")
        print()
        print("请确认:")
        print("  1. 文件路径是否正确")
        print("  2. 文件是否存在于当前目录")
        print("  3. 文件名是否正确（包括扩展名）")
        print()
        input("按回车键退出...")
        return
    
    print(f"找到更新文件: {zip_path}")
    print()
    
    try:
        # 1. 停止服务器
        print("正在停止服务器...")
        subprocess.run([sys.executable, 'stop.py'], capture_output=True)
        print("服务器已停止")
        
        # 2. 创建备份
        print("正在创建备份...")
        backup_dir = os.path.join(os.getcwd(), 'media', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_更新前_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # 备份用户文件
        user_files_path = os.path.join(os.getcwd(), 'media', 'user_files')
        if os.path.exists(user_files_path):
            shutil.copytree(user_files_path, os.path.join(backup_path, 'user_files'))
            print("用户文件备份完成")
        
        # 备份配置文件
        env_file = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file):
            os.makedirs(backup_path, exist_ok=True)
            shutil.copy2(env_file, os.path.join(backup_path, '.env'))
            print("配置文件备份完成")
        
        print(f"备份创建完成: {backup_path}")
        
        # 3. 解压新版本
        print("正在解压新版本...")
        temp_dir = os.path.join(os.getcwd(), 'temp_update')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
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
            print("错误: 未找到项目目录")
            return
        
        # 4. 更新文件
        print("正在更新文件...")
        
        # 需要更新的目录
        update_dirs = [
            'templates', 'static', 'users', 'documents', 
            'system', 'accounts', 'teacher_doc_system'
        ]
        
        # 需要更新的文件
        update_files = [
            'manage.py', 'requirements.txt', 'start_lan.bat',
            'start_local.bat', 'start.py', 'stop.bat', 'stop.py'
        ]
        
        # 更新目录
        for dir_name in update_dirs:
            src_path = os.path.join(project_dir, dir_name)
            dst_path = os.path.join(os.getcwd(), dir_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                print(f"  更新目录: {dir_name}")
        
        # 更新文件
        for file_name in update_files:
            src_path = os.path.join(project_dir, file_name)
            dst_path = os.path.join(os.getcwd(), file_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                shutil.copy2(src_path, dst_path)
                print(f"  更新文件: {file_name}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print("文件更新完成")
        
        # 5. 运行数据库迁移
        print("正在运行数据库迁移...")
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("数据库迁移完成")
        else:
            print("数据库迁移失败，请手动运行: python manage.py migrate")
        
        # 6. 收集静态文件
        print("正在收集静态文件...")
        result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("静态文件收集完成")
        else:
            print("静态文件收集失败，请手动运行: python manage.py collectstatic")
        
        print()
        print("=" * 50)
        print("系统更新成功完成！")
        print("=" * 50)
        print()
        print("下一步操作:")
        print("  1. 启动服务器: python start_lan.py")
        print("  2. 访问系统: http://localhost:8000")
        print("  3. 检查功能是否正常")
        print()
        print(f"备份位置: {backup_path}")
        print("=" * 50)
        
    except Exception as e:
        print()
        print("=" * 50)
        print("系统更新失败！")
        print("=" * 50)
        print()
        print(f"错误信息: {str(e)}")
        print()
        print("故障排除:")
        print("  1. 检查Python环境是否正确")
        print("  2. 确认zip文件格式正确")
        print("  3. 查看错误信息并手动处理")
        print("  4. 如需恢复，请从备份目录恢复")
        print("=" * 50)
    
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()
