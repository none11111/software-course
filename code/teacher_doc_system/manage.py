#!/usr/bin/env python
"""Django的命令行工具"""
import os
import sys

def main():
    """运行管理任务"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teacher_doc_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。请确认已安装Django并在PYTHONPATH环境变量中可用。"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
