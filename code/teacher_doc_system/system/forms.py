from django import forms
from django.core.exceptions import ValidationError
from .models import SystemConfig


class SystemConfigForm(forms.ModelForm):
    """系统配置表单"""
    class Meta:
        model = SystemConfig
        fields = ['key', 'value', 'description']
        widgets = {
            'key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '配置键'
            }),
            'value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '配置值'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '配置描述'
            }),
        }
        labels = {
            'key': '配置键',
            'value': '配置值',
            'description': '配置描述',
        }
    
    def clean_key(self):
        key = self.cleaned_data.get('key')
        if not key or not key.strip():
            raise ValidationError('配置键不能为空')
        
        # 检查键名格式
        if not key.replace('_', '').replace('-', '').isalnum():
            raise ValidationError('配置键只能包含字母、数字、下划线和连字符')
        
        return key.strip()




class UserImportForm(forms.Form):
    """用户导入表单"""
    file = forms.FileField(
        label='CSV文件',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='请上传包含用户信息的CSV文件。必需字段：employee_id, first_name, last_name, email'
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # 检查文件类型
            if not file.name.endswith('.csv'):
                raise ValidationError('请上传CSV格式的文件')
            
            # 检查文件大小（限制为10MB）
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('文件大小不能超过10MB')
        
        return file


class SystemSettingsForm(forms.Form):
    """系统设置表单"""
    # 存储设置
    default_storage_quota = forms.IntegerField(
        label='默认存储配额(GB)',
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='新用户的默认存储配额'
    )
    
    max_file_size = forms.IntegerField(
        label='最大文件大小(MB)',
        min_value=1,
        max_value=2048,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='单个文件的最大上传大小'
    )
    
    # 分享设置
    default_share_expiry_days = forms.IntegerField(
        label='默认分享有效期(天)',
        min_value=1,
        max_value=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='分享链接的默认有效期'
    )
    
    max_share_downloads = forms.IntegerField(
        label='分享链接最大下载次数',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='0表示无限制'
    )
    
    # 安全设置
    password_expiry_days = forms.IntegerField(
        label='密码有效期(天)',
        min_value=30,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='用户密码的有效期'
    )
    
    enable_cas_auth = forms.BooleanField(
        required=False,
        label='启用CAS统一身份认证',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='启用后将支持CAS单点登录'
    )
    
    # 备份设置
    auto_backup_enabled = forms.BooleanField(
        required=False,
        label='启用自动备份',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='系统将自动创建数据备份'
    )
    
    backup_retention_days = forms.IntegerField(
        label='备份保留天数',
        min_value=1,
        max_value=90,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='自动删除超过此天数的备份文件'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # 验证备份设置
        auto_backup_enabled = cleaned_data.get('auto_backup_enabled')
        backup_retention_days = cleaned_data.get('backup_retention_days')
        
        if auto_backup_enabled and backup_retention_days < 7:
            raise ValidationError('启用自动备份时，备份保留天数不能少于7天')
        
        return cleaned_data


class LogFilterForm(forms.Form):
    """日志筛选表单"""
    LEVEL_CHOICES = [
        ('', '所有级别'),
        ('DEBUG', '调试'),
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('CRITICAL', '严重'),
    ]
    
    OPERATION_CHOICES = [
        ('', '所有操作'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('download', '下载'),
        ('view', '查看'),
        ('star', '星标'),
        ('archive', '归档'),
        ('publish', '发布'),
    ]
    
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='日志级别'
    )
    
    operation = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='操作类型'
    )
    
    user = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '用户ID'
        }),
        label='用户ID'
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
    
    ip_address = forms.GenericIPAddressField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'IP地址'
        }),
        label='IP地址'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('开始日期不能晚于结束日期')
        
        return cleaned_data
