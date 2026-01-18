from django.core.management.base import BaseCommand
from documents.models import DocumentCategory
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '创建默认的文档分类'

    def handle(self, *args, **options):
        # 获取或创建管理员用户
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': '系统',
                'last_name': '管理员',
                'email': 'admin@example.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # 默认分类数据
        categories_data = [
            {
                'name': '教学文档',
                'icon': 'fa-graduation-cap',
                'children': [
                    {'name': '课件', 'icon': 'fa-file-powerpoint-o'},
                    {'name': '教学大纲', 'icon': 'fa-list-alt'},
                    {'name': '教案', 'icon': 'fa-book'},
                    {'name': '试卷', 'icon': 'fa-file-text-o'},
                ]
            },
            {
                'name': '科研文档',
                'icon': 'fa-flask',
                'children': [
                    {'name': '论文', 'icon': 'fa-file-text'},
                    {'name': '研究报告', 'icon': 'fa-file-pdf-o'},
                    {'name': '实验数据', 'icon': 'fa-table'},
                    {'name': '项目文档', 'icon': 'fa-folder'},
                ]
            },
            {
                'name': '行政文档',
                'icon': 'fa-briefcase',
                'children': [
                    {'name': '会议记录', 'icon': 'fa-calendar'},
                    {'name': '通知公告', 'icon': 'fa-bullhorn'},
                    {'name': '工作计划', 'icon': 'fa-tasks'},
                    {'name': '总结报告', 'icon': 'fa-file-o'},
                ]
            },
            {
                'name': '学生作业',
                'icon': 'fa-users',
                'children': [
                    {'name': '作业批改', 'icon': 'fa-check-circle'},
                    {'name': '成绩单', 'icon': 'fa-bar-chart'},
                    {'name': '学生作品', 'icon': 'fa-star'},
                ]
            },
            {
                'name': '其他文档',
                'icon': 'fa-folder-o',
                'children': []
            }
        ]
        
        created_count = 0
        
        for category_data in categories_data:
            # 创建父分类
            parent_category, created = DocumentCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'icon': category_data['icon'],
                    'created_by': admin_user,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建分类: {parent_category.name}')
                )
            
            # 创建子分类
            for child_data in category_data['children']:
                child_category, created = DocumentCategory.objects.get_or_create(
                    name=child_data['name'],
                    defaults={
                        'parent': parent_category,
                        'icon': child_data['icon'],
                        'created_by': admin_user,
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'创建子分类: {child_category.name} (父分类: {parent_category.name})')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'成功创建 {created_count} 个文档分类')
        )
