from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(forms.Form):
    """登录表单"""
    username = forms.CharField(
        max_length=150,
        label='账号',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '教师请输入工号，管理员请输入用户名',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='记住登录状态',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('请输入账号')
        return username


class ChangePasswordForm(forms.Form):
    """修改密码表单"""
    old_password = forms.CharField(
        label='原密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入原密码'
        })
    )
    new_password = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入新密码（至少8位，包含字母和数字）'
        }),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请再次输入新密码'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError('两次输入的密码不一致')
            
            # 检查密码复杂度
            if len(new_password) < 8:
                raise ValidationError('密码长度至少为8位')
            
            if not any(c.isalpha() for c in new_password):
                raise ValidationError('密码必须包含字母')
            
            if not any(c.isdigit() for c in new_password):
                raise ValidationError('密码必须包含数字')
        
        return cleaned_data


class ProfileForm(forms.ModelForm):
    """个人信息表单"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'department', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入姓'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入名'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入邮箱地址'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入所属部门'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'first_name': '姓',
            'last_name': '名',
            'email': '邮箱',
            'department': '所属部门',
            'avatar': '头像',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 检查邮箱是否已被其他用户使用
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('该邮箱已被其他用户使用')
        return email
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # 检查文件大小（限制为5MB）
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('头像文件大小不能超过5MB')
            
            # 检查文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar.content_type not in allowed_types:
                raise ValidationError('头像文件格式不支持，请上传JPEG、PNG或GIF格式的图片')
        
        return avatar


class CreateUserForm(forms.ModelForm):
    """创建用户表单（管理员使用）"""
    password = forms.CharField(
        label='初始密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入初始密码'
        }),
        help_text='密码长度至少6位，必须包含字母和数字，不能只使用点号'
    )
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请再次输入密码'
        })
    )
    storage_quota_gb = forms.FloatField(
        label='存储配额(GB)',
        min_value=0,
        initial=10,  # 默认10GB
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '1',
            'placeholder': '请输入存储配额（GB）'
        }),
        help_text='请输入存储配额，单位为GB'
    )
    
    class Meta:
        model = User
        fields = ['username', 'employee_id', 'first_name', 'last_name', 'email', 'department', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工号'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入姓'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入名'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入邮箱地址'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入所属部门'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'username': '用户名',
            'employee_id': '工号',
            'first_name': '姓',
            'last_name': '名',
            'email': '邮箱',
            'department': '所属部门',
            'role': '角色',
        }
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # 检查密码复杂度
            if len(password) < 6:
                raise ValidationError('密码长度至少为6位')
            
            if not any(c.isalpha() for c in password):
                raise ValidationError('密码必须包含字母')
            
            if not any(c.isdigit() for c in password):
                raise ValidationError('密码必须包含数字')
                
            # 检查是否只包含点号
            if password == '.' * len(password):
                raise ValidationError('密码不能只包含点号，请使用字母和数字组合')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('两次输入的密码不一致')
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('该用户名已存在')
        return username
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if User.objects.filter(employee_id=employee_id).exists():
            raise ValidationError('该工号已存在')
        return employee_id
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被使用')
        return email
    
    def clean_storage_quota_gb(self):
        storage_quota_gb = self.cleaned_data.get('storage_quota_gb')
        if storage_quota_gb is not None and storage_quota_gb < 0:
            raise ValidationError('存储配额不能为负数')
        return storage_quota_gb
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        # 将GB转换为字节
        storage_quota_gb = self.cleaned_data.get('storage_quota_gb')
        if storage_quota_gb is not None:
            user.storage_quota = int(storage_quota_gb * (1024 ** 3))
        
        if commit:
            user.save()
        return user


class EditUserForm(forms.ModelForm):
    """编辑用户表单（管理员使用）"""
    storage_quota_gb = forms.FloatField(
        label='存储配额(GB)',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '1',
            'placeholder': '请输入存储配额（GB）'
        }),
        help_text='请输入存储配额，单位为GB'
    )
    
    class Meta:
        model = User
        fields = ['username', 'employee_id', 'first_name', 'last_name', 'email', 'department', 'role', 'is_frozen', 'frozen_reason']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工号'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_frozen': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'frozen_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入冻结原因（可选）'
            }),
        }
        labels = {
            'username': '用户名',
            'employee_id': '工号',
            'first_name': '姓',
            'last_name': '名',
            'email': '邮箱',
            'department': '所属部门',
            'role': '角色',
            'is_frozen': '是否冻结',
            'frozen_reason': '冻结原因',
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('该用户名已被其他用户使用')
        return username
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and User.objects.filter(employee_id=employee_id).exclude(pk=self.instance.pk).exists():
            raise ValidationError('该工号已被其他用户使用')
        return employee_id
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('该邮箱已被其他用户使用')
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果有实例，将字节转换为GB显示
        if self.instance and self.instance.pk:
            self.fields['storage_quota_gb'].initial = self.instance.storage_quota / (1024 ** 3)
    
    def clean_storage_quota_gb(self):
        storage_quota_gb = self.cleaned_data.get('storage_quota_gb')
        if storage_quota_gb is not None and storage_quota_gb < 0:
            raise ValidationError('存储配额不能为负数')
        return storage_quota_gb
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # 将GB转换为字节
        storage_quota_gb = self.cleaned_data.get('storage_quota_gb')
        if storage_quota_gb is not None:
            user.storage_quota = int(storage_quota_gb * (1024 ** 3))
        
        if commit:
            user.save()
        return user
    
    def clean(self):
        cleaned_data = super().clean()
        is_frozen = cleaned_data.get('is_frozen')
        frozen_reason = cleaned_data.get('frozen_reason')
        
        # 如果冻结账户但没有填写原因，给出警告
        if is_frozen and not frozen_reason:
            self.add_error('frozen_reason', '冻结账户时建议填写冻结原因')
        
        return cleaned_data
