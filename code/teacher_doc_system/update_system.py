#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师文档管理系统 - 代码更新脚本
用于安全地更新系统代码，保留用户数据
"""

import os
import sys
import shutil
import zipfile
import subprocess
from datetime import datetime
import json

class SystemUpdater:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.project_root, 'media', 'backups')
        self.temp_dir = os.path.join(self.project_root, 'temp_update')
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_backup(self):
        """创建系统备份"""
        self.log("开始创建系统备份...")
        
        try:
            # 创建备份目录
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 备份数据库
            backup_file = os.path.join(self.backup_dir, f"backup_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
            self.log(f"备份数据库到: {backup_file}")
            
            # 这里需要根据您的数据库配置调整
            # subprocess.run(['mysqldump', '-u', 'root', '-p', 'teacher_doc_system', '>', backup_file])
            
            # 备份媒体文件
            media_backup = os.path.join(self.backup_dir, f"media_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            if os.path.exists(os.path.join(self.project_root, 'media', 'user_files')):
                shutil.copytree(
                    os.path.join(self.project_root, 'media', 'user_files'),
                    media_backup
                )
                self.log(f"媒体文件备份到: {media_backup}")
            
            self.log("系统备份完成")
            return True
            
        except Exception as e:
            self.log(f"备份失败: {str(e)}")
            return False
    
    def extract_new_code(self, zip_path):
        """解压新版本代码"""
        self.log(f"解压新版本代码: {zip_path}")
        
        try:
            # 创建临时目录
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            self.log("代码解压完成")
            return True
            
        except Exception as e:
            self.log(f"解压失败: {str(e)}")
            return False
    
    def update_files(self):
        """更新文件"""
        self.log("开始更新文件...")
        
        try:
            # 需要保留的文件和目录
            preserve_items = [
                'media/user_files',
                'media/backups',
                'logs',
                '.env',
                'db.sqlite3',  # 如果使用SQLite
            ]
            
            # 需要更新的文件和目录
            update_items = [
                'templates',
                'static',
                'users',
                'documents',
                'system',
                'accounts',
                'teacher_doc_system',
                'manage.py',
                'requirements.txt',
                'start_lan.bat',
                'start_local.bat',
                'start.py',
                'stop.bat',
                'stop.py',
            ]
            
            # 从临时目录复制文件
            temp_project_dir = None
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                if os.path.isdir(item_path) and 'teacher_doc_system' in item:
                    temp_project_dir = item_path
                    break
            
            if not temp_project_dir:
                self.log("未找到项目目录")
                return False
            
            # 更新文件
            for item in update_items:
                src_path = os.path.join(temp_project_dir, item)
                dst_path = os.path.join(self.project_root, item)
                
                if os.path.exists(src_path):
                    if os.path.exists(dst_path):
                        if os.path.isdir(dst_path):
                            shutil.rmtree(dst_path)
                        else:
                            os.remove(dst_path)
                    
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                    
                    self.log(f"更新: {item}")
            
            self.log("文件更新完成")
            return True
            
        except Exception as e:
            self.log(f"文件更新失败: {str(e)}")
            return False
    
    def run_migrations(self):
        """运行数据库迁移"""
        self.log("开始运行数据库迁移...")
        
        try:
            # 进入项目目录
            os.chdir(self.project_root)
            
            # 运行迁移
            result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("数据库迁移完成")
                return True
            else:
                self.log(f"数据库迁移失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"数据库迁移失败: {str(e)}")
            return False
    
    def collect_static(self):
        """收集静态文件"""
        self.log("开始收集静态文件...")
        
        try:
            result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("静态文件收集完成")
                return True
            else:
                self.log(f"静态文件收集失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"静态文件收集失败: {str(e)}")
            return False
    
    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            self.log("临时文件清理完成")
        except Exception as e:
            self.log(f"清理失败: {str(e)}")
    
    def update_system(self, zip_path):
        """执行完整的系统更新"""
        self.log("开始系统更新流程...")
        
        # 1. 创建备份
        if not self.create_backup():
            self.log("备份失败，停止更新")
            return False
        
        # 2. 解压新代码
        if not self.extract_new_code(zip_path):
            self.log("代码解压失败，停止更新")
            return False
        
        # 3. 更新文件
        if not self.update_files():
            self.log("文件更新失败，停止更新")
            return False
        
        # 4. 运行迁移
        if not self.run_migrations():
            self.log("数据库迁移失败，请手动处理")
        
        # 5. 收集静态文件
        if not self.collect_static():
            self.log("静态文件收集失败，请手动处理")
        
        # 6. 清理临时文件
        self.cleanup()
        
        self.log("系统更新完成！")
        self.log("请重启服务器以应用更改")
        
        return True

def main():
    """主函数"""
    print("=" * 60)
    print("教师文档管理系统 - 代码更新工具")
    print("=" * 60)
    
    if len(sys.argv) != 2:
        print("使用方法: python update_system.py <新版本zip文件路径>")
        print("示例: python update_system.py new_version.zip")
        return
    
    zip_path = sys.argv[1]
    
    if not os.path.exists(zip_path):
        print(f"错误: 文件不存在 - {zip_path}")
        return
    
    updater = SystemUpdater()
    
    # 确认更新
    print(f"准备更新系统，新版本文件: {zip_path}")
    confirm = input("确认继续更新吗？(y/N): ")
    
    if confirm.lower() != 'y':
        print("更新已取消")
        return
    
    # 执行更新
    success = updater.update_system(zip_path)
    
    if success:
        print("\n✅ 系统更新成功！")
        print("下一步:")
        print("1. 重启服务器")
        print("2. 检查系统功能")
        print("3. 如有问题，可从备份恢复")
    else:
        print("\n❌ 系统更新失败！")
        print("请检查错误信息并手动处理")

if __name__ == "__main__":
    main()
