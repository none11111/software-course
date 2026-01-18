from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    # 仪表盘
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # 用户管理
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.CreateUserView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', views.EditUserView.as_view(), name='edit_user'),
    path('users/<int:pk>/freeze/', views.FreezeUserView.as_view(), name='freeze_user'),
    path('users/<int:pk>/unfreeze/', views.UnfreezeUserView.as_view(), name='unfreeze_user'),
    
    # 系统配置
    path('config/', views.SystemConfigView.as_view(), name='config'),
    
    
]
