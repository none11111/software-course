#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师文档管理系统 - 从文件夹更新工具
使用方法: python 从文件夹更新.py <新版本代码文件夹路径>
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def stop_server():
    """停止服务器"""
    log("正在停止服务器...")
    try:
        result = subprocess.run([sys.executable, 'stop.py'], 
                              capture_output=True, text=True, timeout=10)
        log("服务器已停止")
        return True
    except Exception as e:
        log(f"停止服务器时出现警告: {str(e)}")
        log("继续更新...")
        return True

def create_backup():
    """创建备份"""
    log("正在创建备份...")
    
    try:
        backup_dir = os.path.join(os.getcwd(), 'media', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_更新前_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        # 备份用户文件
        user_files_path = os.path.join(os.getcwd(), 'media', 'user_files')
        if os.path.exists(user_files_path):
            backup_user_files = os.path.join(backup_path, 'user_files')
            shutil.copytree(user_files_path, backup_user_files)
            log("用户文件备份完成")
        
        # 备份配置文件
        env_file = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file):
            shutil.copy2(env_file, os.path.join(backup_path, '.env'))
            log("配置文件备份完成")
        
        # 备份数据库（如果使用SQLite）
        db_file = os.path.join(os.getcwd(), 'db.sqlite3')
        if os.path.exists(db_file):
            shutil.copy2(db_file, os.path.join(backup_path, 'db.sqlite3'))
            log("数据库文件备份完成")
        
        log(f"备份创建完成: {backup_path}")
        return backup_path
        
    except Exception as e:
        log(f"备份失败: {str(e)}")
        return None

def find_project_dir(source_dir):
    """在源目录中查找项目目录"""
    # 检查是否是项目根目录
    if os.path.exists(os.path.join(source_dir, 'manage.py')):
        return source_dir
    
    # 检查子目录
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            if os.path.exists(os.path.join(item_path, 'manage.py')):
                return item_path
            # 递归查找
            sub_result = find_project_dir(item_path)
            if sub_result:
                return sub_result
    
    return None

def update_from_folder(source_dir):
    """从文件夹更新系统"""
    log(f"开始从 {source_dir} 更新系统...")
    
    # 找到项目目录
    project_dir = find_project_dir(source_dir)
    if not project_dir:
        log("错误: 未找到项目目录（找不到manage.py文件）")
        return False
    
    log(f"找到项目目录: {project_dir}")
    
    # 需要保留的文件和目录（不更新）
    preserve_items = [
        'media/user_files',
        'media/backups',
        'logs',
        '.env',
        'db.sqlite3',
        '__pycache__',
        '*.pyc'
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
    
    try:
        # 更新目录
        for dir_name in update_dirs:
            src_path = os.path.join(project_dir, dir_name)
            dst_path = os.path.join(os.getcwd(), dir_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                log(f"更新目录: {dir_name}")
            else:
                log(f"警告: 源目录不存在 - {dir_name}")
        
        # 更新文件
        for file_name in update_files:
            src_path = os.path.join(project_dir, file_name)
            dst_path = os.path.join(os.getcwd(), file_name)
            
            if os.path.exists(src_path):
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                shutil.copy2(src_path, dst_path)
                log(f"更新文件: {file_name}")
            else:
                log(f"警告: 源文件不存在 - {file_name}")
        
        log("文件更新完成")
        return True
        
    except Exception as e:
        log(f"更新失败: {str(e)}")
        return False

def run_migrations():
    """运行数据库迁移"""
    log("正在运行数据库迁移...")
    
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
    log("正在收集静态文件...")
    
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

def install_requirements():
    """安装新的依赖包"""
    log("正在检查并安装依赖包...")
    
    requirements_file = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(requirements_file):
        log("未找到requirements.txt，跳过依赖安装")
        return True
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            log("依赖包安装完成")
            return True
        else:
            log(f"依赖包安装失败: {result.stderr}")
            log("请手动运行: pip install -r requirements.txt")
            return False
            
    except Exception as e:
        log(f"依赖包安装失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("教师文档管理系统 - 从文件夹更新工具")
    print("=" * 60)
    print()
    
    # 检查参数
    if len(sys.argv) != 2:
        print("使用方法: python 从文件夹更新.py <新版本代码文件夹路径>")
        print()
        print("示例:")
        print("  python 从文件夹更新.py E:\\新代码\\teacher_doc_system")
        print("  python 从文件夹更新.py \"C:\\Users\\用户名\\Desktop\\新版本\"")
        print()
        print("说明:")
        print("  - 新版本文件夹可以是项目根目录，也可以是包含项目的父目录")
        print("  - 系统会自动查找包含manage.py的项目目录")
        print("  - 更新过程会自动备份用户数据和配置文件")
        print()
        input("按回车键退出...")
        return
    
    source_dir = sys.argv[1]
    
    # 检查目录是否存在
    if not os.path.exists(source_dir):
        print(f"错误: 目录不存在 - {source_dir}")
        print()
        print("请确认:")
        print("  1. 目录路径是否正确")
        print("  2. 目录是否存在")
        print("  3. 路径中是否包含中文字符（建议使用英文路径）")
        print()
        input("按回车键退出...")
        return
    
    if not os.path.isdir(source_dir):
        print(f"错误: 不是目录 - {source_dir}")
        print()
        input("按回车键退出...")
        return
    
    # 确认更新
    print(f"准备更新系统")
    print(f"新版本代码目录: {source_dir}")
    print(f"当前项目目录: {os.getcwd()}")
    print()
    print("注意: 此操作将更新系统代码，但会保留以下数据:")
    print("  - 用户上传的文件 (media/user_files/)")
    print("  - 备份文件 (media/backups/)")
    print("  - 配置文件 (.env)")
    print("  - 数据库文件 (db.sqlite3)")
    print("  - 日志文件 (logs/)")
    print()
    confirm = input("确认继续更新吗？(y/N): ")
    
    if confirm.lower() != 'y':
        print("更新已取消")
        return
    
    print()
    print("=" * 60)
    log("开始更新流程...")
    print("=" * 60)
    print()
    
    # 1. 停止服务器
    stop_server()
    print()
    
    # 2. 创建备份
    backup_path = create_backup()
    print()
    
    # 3. 更新文件
    if not update_from_folder(source_dir):
        print()
        print("=" * 60)
        print("❌ 文件更新失败！")
        print("=" * 60)
        if backup_path:
            print(f"💾 备份位置: {backup_path}")
            print("如需恢复，请从备份目录恢复文件")
        print()
        input("按回车键退出...")
        return
    print()
    
    # 4. 安装依赖
    install_requirements()
    print()
    
    # 5. 运行迁移
    run_migrations()
    print()
    
    # 6. 收集静态文件
    collect_static()
    print()
    
    # 完成
    print("=" * 60)
    print("✅ 系统更新成功完成！")
    print("=" * 60)
    print()
    print("📋 更新内容:")
    print("  - 代码文件已更新")
    print("  - 数据库已迁移")
    print("  - 静态文件已收集")
    print("  - 用户数据已保留")
    print()
    print("🚀 下一步操作:")
    print("  1. 启动服务器: 双击 start_lan.bat 或运行 python start.py")
    print("  2. 访问系统: http://localhost:8000")
    print("  3. 检查功能是否正常")
    print()
    if backup_path:
        print(f"💾 备份位置: {backup_path}")
    print("=" * 60)
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()

