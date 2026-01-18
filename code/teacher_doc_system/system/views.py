from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Count, Q, Sum
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
import json
import csv
import io
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth import get_user_model

User = get_user_model()
from users.models import UserOperationLog, LoginLog
from users.forms import CreateUserForm, EditUserForm
from documents.models import Document, DocumentOperationLog
from .models import SystemConfig, SystemLog, ShareLink
from .forms import SystemConfigForm
from .utils import require_admin


class AdminRequiredMixin(UserPassesTestMixin):
    """管理员权限检查Mixin"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()
    
    def handle_no_permission(self):
        messages.error(self.request, '您没有权限访问此页面')
        return redirect('documents:document_list')


class DashboardView(AdminRequiredMixin, TemplateView):
    """系统仪表盘"""
    template_name = 'system/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 基础统计
        total_users = User.objects.count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_admins = User.objects.filter(role='admin').count()
        frozen_users = User.objects.filter(is_frozen=True).count()
        
        # 文档统计
        total_documents = Document.objects.count()
        public_documents = Document.objects.filter(is_public=True).count()
        pending_reviews = Document.objects.filter(status='review').count()
        total_downloads = Document.objects.aggregate(
            total=Sum('download_count')
        )['total'] or 0
        
        # 用户存储使用情况 - 获取所有用户的存储信息
        users_storage = []
        for user in User.objects.all().order_by('-storage_used'):
            users_storage.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'storage_quota': user.storage_quota,
                'storage_used': user.storage_used,
                'storage_remaining': max(0, user.storage_quota - user.storage_used),
                'storage_percentage': user.storage_usage_percentage,
                'is_frozen': user.is_frozen
            })
        
        # 计算总体存储统计
        total_storage_quota = sum(user['storage_quota'] for user in users_storage)
        total_storage_used = sum(user['storage_used'] for user in users_storage)
        total_storage_remaining = max(0, total_storage_quota - total_storage_used)
        
        # 计算总体存储使用百分比
        overall_storage_percentage = 0
        if total_storage_quota > 0:
            percentage = (total_storage_used / total_storage_quota) * 100
            if percentage > 0 and percentage < 0.01:
                overall_storage_percentage = 0.01
            else:
                overall_storage_percentage = round(percentage, 2)
        
        # 最近活动
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_logins = LoginLog.objects.filter(
            is_successful=True
        ).order_by('-login_time')[:10]
        
        # 异常情况
        failed_logins = LoginLog.objects.filter(
            is_successful=False,
            login_time__gte=timezone.now() - timezone.timedelta(days=1)
        ).count()
        
        context.update({
            'total_users': total_users,
            'total_teachers': total_teachers,
            'total_admins': total_admins,
            'frozen_users': frozen_users,
            'total_documents': total_documents,
            'public_documents': public_documents,
            'pending_reviews': pending_reviews,
            'total_downloads': total_downloads,
            'users_storage': users_storage,
            'overall_storage_stats': {
                'total_quota': total_storage_quota,
                'total_used': total_storage_used,
                'remaining': total_storage_remaining,
                'percentage': overall_storage_percentage
            },
            'recent_users': recent_users,
            'recent_logins': recent_logins,
            'failed_logins': failed_logins,
        })
        
        return context


class UserListView(AdminRequiredMixin, ListView):
    """用户列表"""
    model = User
    template_name = 'system/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # 筛选条件
        role_filter = self.request.GET.get('role')
        department_filter = self.request.GET.get('department')
        status_filter = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        if department_filter:
            queryset = queryset.filter(department__icontains=department_filter)
        
        if status_filter == 'frozen':
            queryset = queryset.filter(is_frozen=True)
        elif status_filter == 'active':
            queryset = queryset.filter(is_frozen=False)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 添加筛选选项
        departments = User.objects.exclude(
            department__isnull=True
        ).exclude(
            department__exact=''
        ).values_list('department', flat=True).distinct()
        
        context.update({
            'roles': User.ROLE_CHOICES,
            'departments': departments,
            'filters': {
                'role': self.request.GET.get('role'),
                'department': self.request.GET.get('department'),
                'status': self.request.GET.get('status'),
                'search': self.request.GET.get('search'),
            }
        })
        
        return context


class CreateUserView(AdminRequiredMixin, CreateView):
    """创建用户"""
    model = User
    form_class = CreateUserForm
    template_name = 'system/create_user.html'
    success_url = reverse_lazy('system:user_list')
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # 创建用户
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                
                # 设置存储配额（从系统配置获取）
                default_storage_quota = SystemConfig.get_value('default_storage_quota', '10')
                try:
                    default_quota_gb = int(default_storage_quota)
                    user.storage_quota = default_quota_gb * 1024 * 1024 * 1024  # 转换为字节
                except (ValueError, TypeError):
                    user.storage_quota = 10 * 1024 * 1024 * 1024  # 默认10GB
                
                user.save()
                
                # 记录操作日志
                UserOperationLog.objects.create(
                    user=user,
                    operation='create',
                    operated_by=self.request.user,
                    ip_address=self._get_client_ip(),
                    user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                    details={'created_by_admin': True}
                )
                
                messages.success(self.request, f'用户 {user.get_full_name()} 创建成功')
            
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'创建用户失败: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """处理表单验证失败"""
        # 添加详细的错误信息
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        
        if error_messages:
            messages.error(self.request, f'表单验证失败: {"; ".join(error_messages)}')
        else:
            messages.error(self.request, '请检查表单中的错误信息')
        
        return super().form_invalid(form)
    
    def _get_client_ip(self):
        """获取客户端IP地址"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class EditUserView(AdminRequiredMixin, UpdateView):
    """编辑用户"""
    model = User
    form_class = EditUserForm
    template_name = 'system/edit_user.html'
    success_url = reverse_lazy('system:user_list')
    
    def form_valid(self, form):
        with transaction.atomic():
            old_user = User.objects.get(pk=self.object.pk)
            user = form.save()
            
            # 检查是否修改了冻结状态
            if old_user.is_frozen != user.is_frozen:
                if user.is_frozen:
                    user.freeze_account(
                        reason=form.cleaned_data.get('frozen_reason', ''),
                        frozen_by=self.request.user
                    )
                else:
                    user.unfreeze_account(unfrozen_by=self.request.user)
            
            # 记录操作日志
            UserOperationLog.objects.create(
                user=user,
                operation='update',
                operated_by=self.request.user,
                ip_address=self._get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                details={'changes': form.changed_data}
            )
            
            messages.success(self.request, f'用户 {user.get_full_name()} 信息更新成功')
        
        return super().form_valid(form)
    
    def _get_client_ip(self):
        """获取客户端IP地址"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class FreezeUserView(AdminRequiredMixin, View):
    """冻结用户"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        reason = request.POST.get('reason', '')
        
        if user == request.user:
            messages.error(request, '不能冻结自己的账户')
            return redirect('system:user_list')
        
        user.freeze_account(reason=reason, frozen_by=request.user)
        messages.success(request, f'用户 {user.get_full_name()} 已冻结')
        
        return redirect('system:user_list')


class UnfreezeUserView(AdminRequiredMixin, View):
    """解冻用户"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        user.unfreeze_account(unfrozen_by=request.user)
        messages.success(request, f'用户 {user.get_full_name()} 已解冻')
        
        return redirect('system:user_list')







    

class SystemConfigView(AdminRequiredMixin, View):
    """系统配置"""
    
    def get(self, request):
        # 获取或创建默认配置
        default_configs = {
            'max_file_size': '5120',  # 5GB in MB
            'default_storage_quota': '10',  # 10GB
            'password_expiry_days': '90',
            'share_link_expiry_days': '7',
            'backup_retention_days': '7',
            'auto_backup_enabled': 'False',
            'allowed_file_types': 'pdf,doc,docx,ppt,pptx,xls,xlsx,txt,md,zip,rar,7z,jpg,jpeg,png,gif'
        }
        
        # 确保所有配置都存在
        for key, default_value in default_configs.items():
            SystemConfig.objects.get_or_create(
                key=key,
                defaults={'value': default_value, 'description': f'{key}配置'}
            )
        
        # 获取所有配置
        configs = SystemConfig.objects.all().order_by('key')
        
        # 创建表单数据字典
        form_data = {}
        for config in configs:
            form_data[config.key] = config.value
        
        return render(request, 'system/config.html', {
            'configs': configs,
            'form_data': form_data
        })
    
    def post(self, request):
        # 更新配置值
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                # 处理复选框
                if key == 'auto_backup_enabled':
                    value = 'True' if value else 'False'
                SystemConfig.set_value(key, value)
        
        messages.success(request, '系统配置更新成功')
        return redirect('system:config')



