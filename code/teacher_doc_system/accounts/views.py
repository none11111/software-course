# views.py
import json
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()
from .serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
import logging

@csrf_exempt
def cas_login(request):
    """CAS登录验证"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 允许用工号或用户名登录：前端字段沿用 employee_id 名称
            login_identifier = (data.get('employee_id') or '').strip()
            password = data.get('password')
            
            # 根据输入类型选择登录方式
            user = None
            if login_identifier.isdigit():
                # 工号登录（教师）
                user = User.objects.filter(employee_id=login_identifier).first()
                if user and user.role != 'teacher':
                    user = None
            else:
                # 用户名登录（管理员）
                user = User.objects.filter(username=login_identifier).first()
                if user and user.role == 'teacher':
                    user = None
            if user and user.check_password(password):
                if user.is_frozen:
                    return JsonResponse({
                        'success': False,
                        'message': '账户已被冻结，请联系管理员'
                    })
                
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                
                # 记录登录日志
                logging.getLogger('django').info(f"用户 {user.username} 登录系统")
                
                return JsonResponse({
                    'success': True,
                    'message': '登录成功',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role,
                        'employee_id': user.employee_id
                    },
                    'redirect_url': '/documents/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '工号或密码错误'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'登录失败: {str(e)}'
            })
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    """用户退出登录"""
    logout(request)
    return redirect('cas_login')

@login_required
def user_profile(request):
    """用户个人信息页面"""
    user = request.user
    storage_used_gb = user.used_storage / (1024 ** 3)
    storage_quota_gb = user.storage_quota / (1024 ** 3)
    storage_percent = (storage_used_gb / storage_quota_gb) * 100 if storage_quota_gb > 0 else 0
    
    context = {
        'user': user,
        'storage_used_gb': round(storage_used_gb, 2),
        'storage_quota_gb': round(storage_quota_gb, 2),
        'storage_percent': round(storage_percent, 2),
    }
    return render(request, 'accounts/user_profile.html', context)

@login_required
@require_http_methods(["GET"])
def get_user_info(request):
    """获取用户信息API"""
    user = request.user
    return JsonResponse({
        'success': True,
        'data': UserSerializer(user).data
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """更新用户资料"""
    try:
        data = json.loads(request.body)
        user = request.user
        
        with transaction.atomic():
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.department = data.get('department', user.department)
            user.save()
            
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.bio = data.get('bio', profile.bio)
            profile.teaching_courses = data.get('teaching_courses', profile.teaching_courses)
            profile.save()
        
        return JsonResponse({
            'success': True,
            'message': '资料更新成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'更新失败: {str(e)}'
        })
