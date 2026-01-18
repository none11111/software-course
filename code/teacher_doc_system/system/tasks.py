from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
import os
import zipfile
import tempfile
import shutil
import json
from .models import Backup, SystemLog


def create_backup_task(backup_id):
    """创建数据备份任务"""
    try:
        backup = Backup.objects.get(id=backup_id)
        backup.status = 'running'
        backup.save()
        
        print(f"开始创建备份: {backup.name}")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        backup_file = os.path.join(temp_dir, f'backup_{backup.name}.zip')
        
        print(f"临时目录: {temp_dir}")
        print(f"备份文件: {backup_file}")
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 备份数据库信息
            db_info = {
                'database': settings.DATABASES['default']['NAME'],
                'backup_time': timezone.now().isoformat(),
                'backup_name': backup.name,
                'description': backup.description,
            }
            
            # 将数据库信息写入文件
            db_info_file = os.path.join(temp_dir, 'database_info.json')
            with open(db_info_file, 'w', encoding='utf-8') as f:
                json.dump(db_info, f, ensure_ascii=False, indent=2)
            
            zipf.write(db_info_file, 'database_info.json')
            print("数据库信息已添加到备份")
            
            # 备份媒体文件（如果存在，排除备份目录）
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                print(f"开始备份媒体文件: {media_root}")
                file_count = 0
                for root, dirs, files in os.walk(media_root):
                    # 排除备份目录，避免递归备份
                    if 'backups' in dirs:
                        dirs.remove('backups')
                        print("已排除备份目录，避免递归备份")
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            arcname = os.path.relpath(file_path, media_root)
                            zipf.write(file_path, f'media/{arcname}')
                            file_count += 1
                            if file_count % 10 == 0:
                                print(f"已备份 {file_count} 个文件")
                        except Exception as e:
                            print(f"跳过文件 {file_path}: {e}")
                            continue
                print(f"媒体文件备份完成，共 {file_count} 个文件")
            else:
                print(f"媒体目录不存在: {media_root}")
                # 即使媒体目录不存在，也创建一个空的备份
                print("创建空的媒体文件备份")
        
        print(f"ZIP文件创建完成: {backup_file}")
        print(f"ZIP文件大小: {os.path.getsize(backup_file)} bytes")
        
        # 保存备份文件到media目录
        
        # 创建备份目录
        backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        print(f"备份目录: {backup_dir}")
        
        # 生成备份文件名
        backup_filename = f'backup_{backup.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip'
        backup_dest_path = os.path.join(backup_dir, backup_filename)
        
        # 移动文件到最终位置
        shutil.move(backup_file, backup_dest_path)
        print(f"文件已移动到: {backup_dest_path}")
        
        # 更新备份记录
        backup.file_path = f'backups/{backup_filename}'
        backup.file_size = os.path.getsize(backup_dest_path)
        backup.status = 'completed'
        backup.completed_at = timezone.now()
        backup.save()
        
        print(f"备份完成: {backup_dest_path}, 大小: {backup.file_size} bytes")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print("临时目录已清理")
        
        # 记录成功日志
        SystemLog.objects.create(
            level='INFO',
            message=f'备份 {backup.name} 创建成功，文件大小: {backup.file_size} bytes',
            module='backup'
        )
        
        return f'备份 {backup.name} 创建成功'
    
    except Exception as e:
        print(f"备份失败: {e}")
        import traceback
        error_trace = traceback.format_exc()
        print(f"错误详情: {error_trace}")
        
        # 更新备份状态为失败
        try:
            backup = Backup.objects.get(id=backup_id)
            backup.status = 'failed'
            backup.error_message = f"{str(e)}\n\n详细错误:\n{error_trace}"
            backup.save()
            print(f"备份状态已更新为失败: {backup.name}")
        except Backup.DoesNotExist:
            print(f"找不到备份记录: {backup_id}")
        
        # 记录错误日志
        try:
            SystemLog.objects.create(
                level='ERROR',
                message=f'备份创建失败: {str(e)}',
                module='backup'
            )
            print("错误日志已记录")
        except Exception as log_error:
            print(f"记录日志失败: {log_error}")
        
        raise e




@shared_task
def cleanup_expired_share_links():
    """清理过期分享链接任务"""
    try:
        from .models import ShareLink
        
        # 查找过期的分享链接
        expired_links = ShareLink.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        
        expired_count = 0
        for link in expired_links:
            link.is_active = False
            link.save()
            expired_count += 1
        
        # 记录清理日志
        SystemLog.objects.create(
            level='INFO',
            message=f'清理了 {expired_count} 个过期分享链接',
            module='share_cleanup',
            details={'expired_count': expired_count}
        )
        
        return f'清理了 {expired_count} 个过期分享链接'
    
    except Exception as e:
        SystemLog.objects.create(
            level='ERROR',
            message=f'清理过期分享链接失败: {str(e)}',
            module='share_cleanup'
        )
        raise e
