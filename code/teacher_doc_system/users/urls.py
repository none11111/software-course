from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # 个人中心
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    
    # 登录记录
    path('login-logs/', views.LoginLogsView.as_view(), name='login_logs'),
]
