# documents/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DocumentCategory(models.Model):
    """文档分类（如教学文档、科研文档、行政文档等）"""
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='children', 
        verbose_name="父分类"
    )  # 支持二级分类（如教学文档→课件/大纲）
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标标识")  # 前端显示用（如FontAwesome图标）
    is_active = models.BooleanField(default=True, verbose_name="是否启用")  # 支持分类停用
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_categories', 
        verbose_name="创建人"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "文档分类"
        verbose_name_plural = "文档分类"
        ordering = ['name']  # 按名称排序，便于管理

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        """返回分类完整路径（如“教学文档→课件”）"""
        if self.parent:
            return f"{self.parent.full_path}→{self.name}"
        return self.name
    
    # documents/models.py
class Document(models.Model):
    """文档核心信息模型"""
    STATUS_CHOICES = (
        ('draft', '草稿'),      # 未完成，仅自己可见
        ('review', '待审核'),   # 需管理员审核（可选流程）
        ('published', '已发布'), # 审核通过/直接发布，按权限可见
        ('archived', '已归档'),  # 不再更新，保留历史
        ('rejected', '审核未通过'), # 审核被拒绝，教师可重新提交
    )
    title = models.CharField(max_length=255, verbose_name="文档标题")
    category = models.ForeignKey(
        DocumentCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='documents', 
        verbose_name="所属分类"
    )
    description = models.TextField(blank=True, verbose_name="文档描述")
    file = models.FileField(
        upload_to='user_files/%Y/%m/%d/', 
        verbose_name="文档文件"
    )  # 文件会保存在 MEDIA_ROOT/user_files/ 目录下
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)")  # 用于前端显示和大小校验（关联.env的MAX_FILE_SIZE）
    file_type = models.CharField(max_length=20, verbose_name="文件类型")  # 如pdf、docx、zip（提取自文件后缀）
    file_hash = models.CharField(max_length=64, unique=True, verbose_name="文件哈希值")  # 用于去重（MD5/SHA256）
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='authored_documents', 
        verbose_name="作者"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")  # 公开后所有教师可见
    is_starred = models.BooleanField(default=False, verbose_name="是否星标")  # 个人收藏功能
    download_count = models.PositiveIntegerField(default=0, verbose_name="下载次数")
    view_count = models.PositiveIntegerField(default=0, verbose_name="查看次数")  # 统计浏览量
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    archived_at = models.DateTimeField(null=True, blank=True, verbose_name="归档时间")  # 记录归档时间

    class Meta:
        verbose_name = "文档"
        verbose_name_plural = "文档"
        indexes = [
            models.Index(fields=['author', 'status']),  # 作者查询自己的文档（高频）
            models.Index(fields=['category', 'status']),  # 按分类筛选文档
            models.Index(fields=['is_public', 'status']),  # 快速查询公开文档
            models.Index(fields=['created_at']),  # 按时间排序（最新/最热）
        ]

    def __str__(self):
        return f"{self.title}（{self.file_type}）"
    

    # documents/models.py
class DocumentVersion(models.Model):
    """文档版本历史（解决频繁修改场景）"""
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='versions', 
        verbose_name="关联文档"
    )
    version_number = models.CharField(max_length=10, verbose_name="版本号")  # 如v1.0、v2.1（比Decimal更灵活）
    file = models.FileField(
        upload_to='user_files/versions/%Y/%m/%d/', 
        verbose_name="版本文件"
    )  # 文件会保存在 MEDIA_ROOT/user_files/versions/ 目录下
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)")
    change_log = models.TextField(blank=True, verbose_name="更新日志")  # 记录修改内容（强制填写，增强可追溯性）
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="更新人"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "文档版本"
        verbose_name_plural = "文档版本"
        unique_together = ('document', 'version_number')  # 同一文档版本号唯一
        ordering = ['-created_at']  # 默认显示最新版本

    def __str__(self):
        return f"{self.document.title} - {self.version_number}"
    
    # documents/models.py
class DocumentOperationLog(models.Model):
    """文档操作日志（满足审计和追溯需求）"""
    OPERATION_CHOICES = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('download', '下载'),
        ('view', '查看'),
        ('star', '星标'),
        ('archive', '归档'),
        ('publish', '发布'),
    )
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='operation_logs', 
        verbose_name="关联文档"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='document_operations', 
        verbose_name="操作人"
    )
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, verbose_name="操作类型")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="操作IP")  # 记录操作来源
    details = models.JSONField(blank=True, null=True, verbose_name="操作详情")  # 存储额外信息（如旧状态→新状态）
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        verbose_name = "文档操作日志"
        verbose_name_plural = "文档操作日志"
        indexes = [
            models.Index(fields=['user', 'operation']),  # 按用户查询操作记录
            models.Index(fields=['document', 'created_at']),  # 按文档查询历史操作
        ]
        ordering = ['-created_at']  # 默认显示最新操作