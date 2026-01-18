from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView, UpdateView
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.db.models import Q
import json

from django.contrib.auth import get_user_model
from .models import UserOperationLog, LoginLog

User = get_user_model()
from .forms import LoginForm, ChangePasswordForm, ProfileForm


class LoginView(View):
    """统一登录页面"""
    template_name = 'users/login.html'
    form_class = LoginForm
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect_by_role(request.user)
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            # 去除前后空格，避免因误输空格导致的校验失败
            username = (form.cleaned_data['username'] or '').strip()
            password = (form.cleaned_data['password'] or '').strip()
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # 尝试通过工号或用户名登录（保持原有规则：教师=工号，管理员=用户名）
            user = None
            if username.isdigit():
                # 工号登录（教师）
                try:
                    user = User.objects.get(employee_id=username)
                    # 检查用户角色，只有教师才能用工号登录
                    if user.role != 'teacher':
                        user = None
                        messages.error(request, '工号只能用于教师登录')
                except User.DoesNotExist:
                    pass
            else:
                # 用户名登录（管理员）
                try:
                    user = User.objects.get(username=username)
                    # 检查用户角色，只有管理员才能用用户名登录
                    if user.role == 'teacher':
                        user = None
                        messages.error(request, '教师请使用工号登录')
                except User.DoesNotExist:
                    pass
            
            if user and user.check_password(password):
                if user.is_frozen:
                    messages.error(request, '账户已冻结，请联系管理员')
                    self._log_login_attempt(user, request, False, '账户已冻结')
                    return render(request, self.template_name, {'form': form})
                
                # 登录成功
                login(request, user)
                
                # 更新登录信息
                user.last_login_ip = self._get_client_ip(request)
                user.save()
                
                # 记录登录日志
                self._log_login_attempt(user, request, True)
                
                # 设置会话过期时间
                if not remember_me:
                    request.session.set_expiry(0)  # 浏览器关闭时过期
                else:
                    request.session.set_expiry(7 * 24 * 60 * 60)  # 7天
                
                # 根据角色重定向
                return self._redirect_by_role(user)
            else:
                messages.error(request, '账号或密码错误')
                if user:
                    self._log_login_attempt(user, request, False, '密码错误')
        
        return render(request, self.template_name, {'form': form})
    
    def _redirect_by_role(self, user):
        """根据用户角色重定向"""
        if user.role == 'admin':
            return redirect('system:dashboard')
        else:
            return redirect('documents:document_list')
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_login_attempt(self, user, request, is_successful, failure_reason=''):
        """记录登录尝试"""
        LoginLog.objects.create(
            user=user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_successful=is_successful,
            failure_reason=failure_reason
        )


class LogoutView(View):
    """登出视图"""
    
    def get(self, request):
        if request.user.is_authenticated:
            # 记录登出日志
            LoginLog.objects.filter(
                user=request.user,
                logout_time__isnull=True
            ).update(logout_time=timezone.now())
        
        logout(request)
        messages.success(request, '已成功登出')
        return redirect('users:login')


class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码视图"""
    template_name = 'users/change_password.html'
    form_class = ChangePasswordForm
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            
            if not request.user.check_password(old_password):
                messages.error(request, '原密码错误')
                return render(request, self.template_name, {'form': form})
            
            # 更新密码
            request.user.set_password(new_password)
            request.user.must_change_password = False
            request.user.password_changed_at = timezone.now()
            request.user.save()
            
            # 记录操作日志
            UserOperationLog.objects.create(
                user=request.user,
                operation='update',
                operated_by=request.user,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'action': 'password_change'}
            )
            
            messages.success(request, '密码修改成功')
            return redirect('users:profile')
        
        return render(request, self.template_name, {'form': form})
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ProfileView(LoginRequiredMixin, TemplateView):
    """个人中心视图"""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 获取最近的登录记录
        recent_logins = LoginLog.objects.filter(user=user).order_by('-login_time')[:10]
        
        # 获取存储使用情况
        storage_info = {
            'quota': user.storage_quota,
            'used': user.storage_used,
            'remaining': user.storage_remaining,
            'percentage': user.storage_usage_percentage
        }
        
        context.update({
            'user': user,
            'recent_logins': recent_logins,
            'storage_info': storage_info,
        })
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """编辑个人信息视图"""
    model = User
    form_class = ProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        # 记录操作日志
        UserOperationLog.objects.create(
            user=self.request.user,
            operation='update',
            operated_by=self.request.user,
            ip_address=self._get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={'action': 'profile_update', 'changes': form.changed_data}
        )
        
        messages.success(self.request, '个人信息更新成功')
        return super().form_valid(form)
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginLogsView(LoginRequiredMixin, TemplateView):
    """登录记录视图"""
    template_name = 'users/login_logs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取登录记录，支持分页和筛选
        logs = LoginLog.objects.filter(user=self.request.user)
        
        # 按时间筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            logs = logs.filter(login_time__date__gte=start_date)
        if end_date:
            logs = logs.filter(login_time__date__lte=end_date)
        
        # 按IP筛选
        ip_filter = self.request.GET.get('ip')
        if ip_filter:
            logs = logs.filter(ip_address__icontains=ip_filter)
        
        # 按状态筛选
        status_filter = self.request.GET.get('status')
        if status_filter == 'success':
            logs = logs.filter(is_successful=True)
        elif status_filter == 'failed':
            logs = logs.filter(is_successful=False)
        
        logs = logs.order_by('-login_time')[:100]  # 最多显示100条
        
        context.update({
            'logs': logs,
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'ip': ip_filter,
                'status': status_filter,
            }
        })
        return context


# API视图（用于AJAX请求）
@login_required
def check_storage_quota(request):
    """检查存储配额API"""
    user = request.user
    return JsonResponse({
        'quota': user.storage_quota,
        'used': user.storage_used,
        'remaining': user.storage_remaining,
        'percentage': user.storage_usage_percentage
    })


@login_required
def get_user_info(request):
    """获取用户信息API"""
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'employee_id': user.employee_id,
        'full_name': user.get_full_name(),
        'role': user.role,
        'role_display': user.get_role_display(),
        'department': user.department,
        'is_frozen': user.is_frozen,
        'must_change_password': user.must_change_password,
    })
