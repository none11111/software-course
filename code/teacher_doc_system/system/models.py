from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class SystemConfig(models.Model):
    """系统配置模型"""
    key = models.CharField(max_length=100, unique=True, verbose_name="配置键")
    value = models.TextField(verbose_name="配置值")
    description = models.TextField(blank=True, verbose_name="配置描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "系统配置"
        verbose_name_plural = "系统配置"
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    @classmethod
    def get_value(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(key=key)
            return config.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, key, value, description=""):
        """设置配置值"""
        config, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        if not created:
            config.value = value
            config.description = description
            config.save()
        return config


class SystemLog(models.Model):
    """系统日志模型"""
    LEVEL_CHOICES = (
        ('DEBUG', '调试'),
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('CRITICAL', '严重'),
    )
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="日志级别")
    message = models.TextField(verbose_name="日志消息")
    module = models.CharField(max_length=100, blank=True, verbose_name="模块")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        verbose_name="相关用户"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "系统日志"
        verbose_name_plural = "系统日志"
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.level}] {self.message[:50]}"


class ShareLink(models.Model):
    """分享链接模型"""
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='share_links',
        verbose_name="关联文档",
        null=True,
        blank=True
    )
    token = models.CharField(max_length=64, unique=True, verbose_name="分享令牌")
    password = models.CharField(max_length=128, blank=True, verbose_name="访问密码")
    expires_at = models.DateTimeField(verbose_name="过期时间")
    max_downloads = models.PositiveIntegerField(default=0, verbose_name="最大下载次数")
    download_count = models.PositiveIntegerField(default=0, verbose_name="已下载次数")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_share_links',
        verbose_name="创建人",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "分享链接"
        verbose_name_plural = "分享链接"
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at', 'is_active']),
            models.Index(fields=['created_by', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document.title} - {self.token[:8]}..."
    
    @property
    def is_expired(self):
        """检查是否已过期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_available(self):
        """检查是否可用"""
        return (self.is_active and 
                not self.is_expired and 
                (self.max_downloads == 0 or self.download_count < self.max_downloads))
    
    def can_access(self, password=None):
        """检查是否可以访问"""
        if not self.is_available:
            return False
        
        if self.password:
            return self.password == password
        
        return True
