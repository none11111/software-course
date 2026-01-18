# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    """用户模型（区分系统管理员和教师）"""
    ROLE_CHOICES = (
        ('admin', '系统管理员'),  # 拥有全量权限，管理用户和系统配置
        ('teacher', '教师'),       # 管理个人文档，查看公开文档
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher', verbose_name="角色")
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="工号")  # 教师/管理员唯一标识，支持批量导入
    department = models.CharField(max_length=100, blank=True, verbose_name="所属部门")  # 教师所属院系/部门
    avatar = models.ImageField(upload_to='media/avatars/', null=True, blank=True, verbose_name="头像")  # 个人头像
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="最后登录IP")  # 增强审计能力
    
    # 存储配额相关字段
    storage_quota = models.BigIntegerField(default=settings.TEACHER_DOC_SETTINGS['DEFAULT_STORAGE_QUOTA'], verbose_name="存储配额(字节)")
    storage_used = models.BigIntegerField(default=0, verbose_name="已用存储(字节)")
    
    # 账户状态
    is_frozen = models.BooleanField(default=False, verbose_name="是否冻结")
    frozen_reason = models.TextField(blank=True, verbose_name="冻结原因")
    frozen_at = models.DateTimeField(null=True, blank=True, verbose_name="冻结时间")
    
    # 密码管理
    password_changed_at = models.DateTimeField(null=True, blank=True, verbose_name="密码修改时间")
    must_change_password = models.BooleanField(default=True, verbose_name="必须修改密码")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        indexes = [
            models.Index(fields=['role']),  # 按角色快速筛选用户
            models.Index(fields=['employee_id']),  # 工号查询优化（高频操作）
            models.Index(fields=['department']),  # 按部门统计/筛选教师
        ]

    def get_full_name(self):
        """按照中文习惯返回完整姓名（姓氏 + 名字）"""
        if self.last_name and self.first_name:
            return f"{self.last_name}{self.first_name}"
        elif self.last_name:
            return self.last_name
        elif self.first_name:
            return self.first_name
        else:
            return ""
    
    def __str__(self):
        return f"{self.get_full_name() or self.username}（{self.get_role_display()}）"
    
    @property
    def storage_usage_percentage(self):
        """计算存储使用百分比"""
        if self.storage_quota == 0:
            return 0
        percentage = (self.storage_used / self.storage_quota) * 100
        # 如果百分比很小但大于0，至少显示0.01%
        if percentage > 0 and percentage < 0.01:
            return 0.01
        # 如果百分比为0，返回0
        if percentage == 0:
            return 0
        # 其他情况保留2位小数
        return round(percentage, 2)
    
    @property
    def storage_remaining(self):
        """计算剩余存储空间"""
        return max(0, self.storage_quota - self.storage_used)
    
    def can_upload_file(self, file_size):
        """检查是否可以上传指定大小的文件"""
        return self.storage_remaining >= file_size
    
    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin'
    
    def is_teacher(self):
        """判断是否为教师"""
        return self.role == 'teacher'
    
    def freeze_account(self, reason="", frozen_by=None):
        """冻结账户"""
        from django.utils import timezone
        self.is_frozen = True
        self.frozen_reason = reason
        self.frozen_at = timezone.now()
        self.save()
        
        # 记录操作日志
        UserOperationLog.objects.create(
            user=self,
            operation='freeze',
            operated_by=frozen_by,
            details={'reason': reason}
        )
    
    def unfreeze_account(self, unfrozen_by=None):
        """解冻账户"""
        self.is_frozen = False
        self.frozen_reason = ""
        self.frozen_at = None
        self.save()
        
        # 记录操作日志
        UserOperationLog.objects.create(
            user=self,
            operation='unfreeze',
            operated_by=unfrozen_by,
            details={}
        )
    
    def reset_password(self, new_password, reset_by=None):
        """重置密码"""
        from django.utils import timezone
        
        # 使用Django提供的set_password，确保兼容密码算法与校验
        self.set_password(new_password)
        self.must_change_password = True
        self.password_changed_at = timezone.now()
        self.save()
        
        # 记录操作日志
        UserOperationLog.objects.create(
            user=self,
            operation='password_reset',
            operated_by=reset_by,
            details={}
        )


class UserOperationLog(models.Model):
    """用户操作日志（审计追踪）"""
    OPERATION_CHOICES = (
        ('create', '创建账户'),
        ('update', '更新信息'),
        ('delete', '删除账户'),
        ('freeze', '冻结账户'),
        ('unfreeze', '解冻账户'),
        ('password_reset', '重置密码'),
        ('login', '登录'),
        ('logout', '登出'),
    )
    
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='operation_logs',
        verbose_name="操作用户"
    )
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, verbose_name="操作类型")
    operated_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operations_performed',
        verbose_name="操作人"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="操作IP")
    user_agent = models.TextField(blank=True, verbose_name="用户代理")
    details = models.JSONField(blank=True, null=True, verbose_name="操作详情")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    
    class Meta:
        verbose_name = "用户操作日志"
        verbose_name_plural = "用户操作日志"
        indexes = [
            models.Index(fields=['user', 'operation']),
            models.Index(fields=['operated_by', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_operation_display()}"


class LoginLog(models.Model):
    """登录日志"""
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name="用户"
    )
    ip_address = models.GenericIPAddressField(verbose_name="登录IP")
    user_agent = models.TextField(verbose_name="用户代理")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="登录时间")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="登出时间")
    is_successful = models.BooleanField(default=True, verbose_name="是否成功")
    failure_reason = models.CharField(max_length=100, blank=True, verbose_name="失败原因")
    
    class Meta:
        verbose_name = "登录日志"
        verbose_name_plural = "登录日志"
        indexes = [
            models.Index(fields=['user', 'login_time']),
            models.Index(fields=['ip_address', 'login_time']),
        ]
        ordering = ['-login_time']
    
    def __str__(self):
        status = "成功" if self.is_successful else f"失败({self.failure_reason})"
        return f"{self.user.get_full_name()} - {status} - {self.login_time}"