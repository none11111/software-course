from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def require_admin(view_func):
    """管理员权限装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        if not request.user.is_admin():
            messages.error(request, '您没有权限访问此页面')
            return redirect('documents:document_list')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_system_event(level, message, module='', user=None, request=None, details=None):
    """记录系统事件日志"""
    from .models import SystemLog
    
    ip_address = None
    if request:
        ip_address = get_client_ip(request)
    
    SystemLog.objects.create(
        level=level,
        message=message,
        module=module,
        user=user,
        ip_address=ip_address,
        details=details
    )




def get_user_storage_stats(user):
    """获取用户存储统计信息"""
    from documents.models import Document
    
    total_documents = Document.objects.filter(author=user).count()
    total_size = Document.objects.filter(author=user).aggregate(
        total=Sum('file_size')
    )['total'] or 0
    
    # 计算使用百分比
    used_percentage = 0
    if user.storage_quota > 0:
        percentage = (total_size / user.storage_quota) * 100
        # 如果百分比很小，至少显示0.01%
        if percentage > 0 and percentage < 0.01:
            used_percentage = 0.01
        else:
            used_percentage = round(percentage, 2)
    
    return {
        'total_documents': total_documents,
        'total_size': total_size,
        'quota': user.storage_quota,
        'used_percentage': used_percentage,
        'remaining': max(0, user.storage_quota - total_size),
    }


