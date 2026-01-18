from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RoleMiddleware:
    """角色权限中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 在视图处理之前执行
        if request.user.is_authenticated:
            # 检查用户是否被冻结
            if request.user.is_frozen:
                # 如果用户被冻结，强制登出并重定向到登录页
                from django.contrib.auth import logout
                logout(request)
                messages.error(request, '账户已被冻结，请联系管理员')
                return redirect('users:login')
            
            # 检查是否需要强制修改密码
            if (request.user.must_change_password and 
                not request.path.startswith('/users/change-password/') and
                not request.path.startswith('/users/logout/')):
                messages.warning(request, '为了安全起见，请先修改初始密码')
                return redirect('users:change_password')
        
        response = self.get_response(request)
        
        # 在视图处理之后执行
        return response


class AdminRequiredMiddleware:
    """管理员权限中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查管理员权限
        if (request.path.startswith('/system/') and 
            request.user.is_authenticated and 
            not request.user.is_admin()):
            messages.error(request, '您没有权限访问此页面')
            return redirect('documents:document_list')
        
        response = self.get_response(request)
        return response
