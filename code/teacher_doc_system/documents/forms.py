from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q
from .models import Document, DocumentCategory, DocumentVersion
from system.models import ShareLink


class DocumentForm(forms.ModelForm):
    """文档表单"""
    class Meta:
        model = Document
        fields = ['title', 'category', 'description', 'file', 'is_public', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入文档标题'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入文档描述（可选）'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': ','.join([f'.{ext}' for ext in settings.TEACHER_DOC_SETTINGS['ALLOWED_FILE_TYPES']])
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': '文档标题',
            'category': '文档分类',
            'description': '文档描述',
            'file': '选择文件',
            'is_public': '公开文档',
            'status': '文档状态',
        }
    
    def __init__(self, *args, **kwargs):
        # 获取用户信息
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 如果是教师用户，限制状态选择
        if self.user and not (self.user.is_superuser or self.user.is_admin()):
            # 教师用户不能选择"已归档"和"审核未通过"状态
            status_choices = list(Document.STATUS_CHOICES)
            if ('archived', '已归档') in status_choices:
                status_choices.remove(('archived', '已归档'))
            if ('rejected', '审核未通过') in status_choices:
                status_choices.remove(('rejected', '审核未通过'))
            self.fields['status'].choices = status_choices
            
            # 限制分类选择：只能选择管理员创建的分类和自己创建的分类
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_users = User.objects.filter(Q(is_superuser=True) | Q(role='admin'))
            
            self.fields['category'].queryset = DocumentCategory.objects.filter(
                Q(created_by__in=admin_users) | Q(created_by=self.user),
                is_active=True
            ).order_by('name')
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # 检查文件大小
            max_size = settings.TEACHER_DOC_SETTINGS['MAX_FILE_SIZE']
            if file.size > max_size:
                raise ValidationError(f'文件大小不能超过 {max_size // (1024*1024*1024)}GB')
            
            # 检查文件类型
            allowed_types = settings.TEACHER_DOC_SETTINGS['ALLOWED_FILE_TYPES']
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                raise ValidationError(f'不支持的文件类型。支持的格式：{", ".join(allowed_types)}')
            
            # 检查文件名
            if len(file.name) > 255:
                raise ValidationError('文件名过长，请重命名后上传')
        
        return file
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise ValidationError('文档标题不能为空')
        
        if len(title) > 255:
            raise ValidationError('文档标题过长')
        
        return title.strip()


class CategoryForm(forms.ModelForm):
    """文档分类表单"""
    class Meta:
        model = DocumentCategory
        fields = ['name', 'parent', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入分类名称'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '图标标识（如：fa-file-pdf）'
            }),
        }
        labels = {
            'name': '分类名称',
            'parent': '父分类',
            'icon': '图标',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 只显示父分类（没有父分类的分类）
        self.fields['parent'].queryset = DocumentCategory.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('name')
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError('分类名称不能为空')
        
        return name.strip()
    
    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent:
            # 防止循环引用
            if parent == self.instance:
                raise ValidationError('不能将自己设为父分类')
            
            # 检查层级深度（最多2级）
            if parent.parent:
                raise ValidationError('分类层级不能超过2级')
        
        return parent


class VersionForm(forms.ModelForm):
    """版本表单"""
    class Meta:
        model = DocumentVersion
        fields = ['file', 'change_log']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': ','.join([f'.{ext}' for ext in settings.TEACHER_DOC_SETTINGS['ALLOWED_FILE_TYPES']])
            }),
            'change_log': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请描述本次更新的内容'
            }),
        }
        labels = {
            'file': '新版本文件',
            'change_log': '更新说明',
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # 检查文件大小
            max_size = settings.TEACHER_DOC_SETTINGS['MAX_FILE_SIZE']
            if file.size > max_size:
                raise ValidationError(f'文件大小不能超过 {max_size // (1024*1024*1024)}GB')
            
            # 检查文件类型
            allowed_types = settings.TEACHER_DOC_SETTINGS['ALLOWED_FILE_TYPES']
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in allowed_types:
                raise ValidationError(f'不支持的文件类型。支持的格式：{", ".join(allowed_types)}')
        
        return file
    
    def clean_change_log(self):
        change_log = self.cleaned_data.get('change_log')
        if not change_log or not change_log.strip():
            raise ValidationError('请填写更新说明')
        
        return change_log.strip()


class ShareLinkForm(forms.ModelForm):
    """分享链接表单"""
    class Meta:
        model = ShareLink
        fields = ['password', 'expires_at', 'max_downloads']
        widgets = {
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': '访问密码（可选，留空表示无需密码）'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'max_downloads': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '最大下载次数（0表示无限制）'
            }),
        }
        labels = {
            'password': '访问密码',
            'expires_at': '过期时间',
            'max_downloads': '最大下载次数',
        }
    
    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        
        if expires_at:
            from django.utils import timezone
            
            # 过期时间不能早于当前时间
            if expires_at <= timezone.now():
                raise ValidationError('过期时间不能早于当前时间')
            
            # 过期时间不能超过30天
            max_expiry = timezone.now() + timezone.timedelta(days=30)
            if expires_at > max_expiry:
                raise ValidationError('过期时间不能超过30天')
        
        return expires_at
    
    def clean_max_downloads(self):
        max_downloads = self.cleaned_data.get('max_downloads')
        
        if max_downloads is not None and max_downloads < 0:
            raise ValidationError('最大下载次数不能为负数')
        
        return max_downloads


class DocumentSearchForm(forms.Form):
    """文档搜索表单"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索文档标题、描述或作者...'
        }),
        label='搜索关键词'
    )
    
    category = forms.ModelChoiceField(
        queryset=DocumentCategory.objects.filter(is_active=True),
        required=False,
        empty_label='所有分类',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='文档分类'
    )
    
    file_type = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='文件类型'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='开始日期'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='结束日期'
    )
    
    my_docs_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='仅显示我的文档'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 动态设置文件类型选项
        from .models import Document
        file_types = Document.objects.values_list('file_type', flat=True).distinct()
        self.fields['file_type'].choices = [('', '所有类型')] + [(t, t.upper()) for t in file_types]
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('开始日期不能晚于结束日期')
        
        return cleaned_data
