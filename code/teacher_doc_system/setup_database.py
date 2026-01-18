#!/usr/bin/env python
"""
数据库设置脚本
用于创建数据库、执行迁移和创建初始数据
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings
from django.db import connection
from django.contrib.auth import get_user_model

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teacher_doc_system.settings')
django.setup()

User = get_user_model()


def create_database():
    """创建数据库"""
    print("正在创建数据库...")
    
    # 获取数据库配置
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    
    # 连接到MySQL服务器（不指定数据库）
    import pymysql
    
    connection_params = {
        'host': db_config['HOST'],
        'port': int(db_config['PORT']),
        'user': db_config['USER'],
        'password': db_config['PASSWORD'],
        'charset': 'utf8mb4'
    }
    
    try:
        # 连接MySQL服务器
        conn = pymysql.connect(**connection_params)
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {db_name} 创建成功")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"创建数据库失败: {e}")
        sys.exit(1)


def run_migrations():
    """执行数据库迁移"""
    print("正在执行数据库迁移...")
    
    try:
        # 创建迁移文件
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # 执行迁移
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("数据库迁移完成")
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        sys.exit(1)


def create_superuser():
    """创建超级管理员"""
    print("正在创建超级管理员...")
    
    try:
        # 检查是否已存在超级用户
        if User.objects.filter(is_superuser=True).exists():
            print("超级管理员已存在")
            return
        
        # 创建超级管理员
        admin_user = User.objects.create_superuser(
            username='admin',
            employee_id='ADMIN001',
            first_name='系统',
            last_name='管理员',
            email='admin@example.com',
            password='admin123456'
        )
        # 设置额外字段
        admin_user.role = 'admin'
        admin_user.department = '系统管理'
        admin_user.must_change_password = True
        admin_user.save()
        
        print(f"超级管理员创建成功:")
        print(f"用户名: admin")
        print(f"密码: admin123456")
        print("请首次登录后修改密码")
        
    except Exception as e:
        print(f"创建超级管理员失败: {e}")
        sys.exit(1)


def create_sample_data():
    """创建示例数据"""
    print("正在创建示例数据...")
    
    try:
        from documents.models import DocumentCategory
        
        # 创建文档分类
        categories = [
            {'name': '教学文档', 'icon': 'fa-book', 'description': '教学相关文档'},
            {'name': '课件', 'parent': '教学文档', 'icon': 'fa-file-powerpoint-o', 'description': '教学课件'},
            {'name': '教学大纲', 'parent': '教学文档', 'icon': 'fa-list-alt', 'description': '课程教学大纲'},
            {'name': '科研文档', 'icon': 'fa-flask', 'description': '科研相关文档'},
            {'name': '论文', 'parent': '科研文档', 'icon': 'fa-file-text-o', 'description': '学术论文'},
            {'name': '报告', 'parent': '科研文档', 'icon': 'fa-file-pdf-o', 'description': '研究报告'},
            {'name': '行政文档', 'icon': 'fa-building', 'description': '行政管理文档'},
        ]
        
        for cat_data in categories:
            parent = None
            if 'parent' in cat_data:
                parent_name = cat_data.pop('parent')
                parent = DocumentCategory.objects.get(name=parent_name)
            
            category, created = DocumentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'parent': parent,
                    'icon': cat_data.get('icon', ''),
                    'description': cat_data.get('description', ''),
                    'created_by': User.objects.filter(is_superuser=True).first()
                }
            )
            
            if created:
                print(f"创建分类: {category.name}")
        
        print("示例数据创建完成")
        
    except Exception as e:
        print(f"创建示例数据失败: {e}")


def create_directories():
    """创建必要的目录"""
    print("正在创建目录结构...")
    
    directories = [
        'media',
        'media/avatars',
        'media/user_files',
        'media/backups',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'logs',
        'templates',
        'templates/users',
        'templates/documents',
        'templates/system',
        'templates/base',
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")


def main():
    """主函数"""
    print("开始设置教师文档管理系统...")
    
    # 创建目录
    create_directories()
    
    # 创建数据库
    create_database()
    
    # 执行迁移
    run_migrations()
    
    # 创建超级管理员
    create_superuser()
    
    # 创建示例数据
    create_sample_data()
    
    print("\n" + "="*50)
    print("教师文档管理系统设置完成！")
    print("="*50)
    print("访问地址: http://localhost:8000")
    print("管理员账号: admin")
    print("管理员密码: admin123456")
    print("请首次登录后修改密码")
    print("="*50)


if __name__ == '__main__':
    main()
