from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # 教师仪表盘
    path('dashboard/', views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
    
    # 文档列表和搜索
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('search/', views.DocumentSearchView.as_view(), name='document_search'),
    
    # 文档操作
    path('upload/', views.UploadDocumentView.as_view(), name='upload_document'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', views.EditDocumentView.as_view(), name='edit_document'),
    path('<int:pk>/delete/', views.DeleteDocumentView.as_view(), name='delete_document'),
    path('batch-delete/', views.BatchDeleteDocumentsView.as_view(), name='batch_delete_documents'),
    path('<int:pk>/download/', views.DownloadDocumentView.as_view(), name='download_document'),
    path('<int:pk>/preview/', views.DocumentPreviewView.as_view(), name='preview_document'),
    
    # 文档分享
    path('<int:pk>/share/', views.CreateShareLinkView.as_view(), name='create_share_link'),
    path('share/<str:token>/', views.ShareLinkView.as_view(), name='share_link'),
    path('share/<str:token>/download/', views.DownloadShareView.as_view(), name='download_share'),
    path('share-links/', views.ShareLinkListView.as_view(), name='share_link_list'),
    path('share-links/<int:pk>/delete/', views.DeleteShareLinkView.as_view(), name='delete_share_link'),
    path('share-links/<int:pk>/disable/', views.DisableShareLinkView.as_view(), name='disable_share_link'),
    path('share-links/<int:pk>/enable/', views.EnableShareLinkView.as_view(), name='enable_share_link'),
    
    # 版本管理
    path('<int:pk>/versions/', views.DocumentVersionsView.as_view(), name='document_versions'),
    path('<int:pk>/versions/upload/', views.UploadVersionView.as_view(), name='upload_version'),
    path('<int:pk>/versions/<int:version_id>/download/', views.DownloadVersionView.as_view(), name='download_version'),
    path('<int:pk>/versions/<int:version_id>/restore/', views.RestoreVersionView.as_view(), name='restore_version'),
    
    # 分类管理
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CreateCategoryView.as_view(), name='create_category'),
    path('categories/<int:pk>/edit/', views.EditCategoryView.as_view(), name='edit_category'),
    path('categories/<int:pk>/delete/', views.DeleteCategoryView.as_view(), name='delete_category'),
    path('categories/<int:pk>/documents/', views.CategoryDocumentsView.as_view(), name='category_documents'),
    
    # 文档审核（仅管理员）
    path('review/', views.DocumentReviewListView.as_view(), name='document_review_list'),
    path('<int:pk>/review/', views.DocumentReviewView.as_view(), name='document_review'),
    
    # API接口
    path('api/upload-progress/', views.UploadProgressAPIView.as_view(), name='upload_progress_api'),
    path('api/document-info/<int:pk>/', views.DocumentInfoAPIView.as_view(), name='document_info_api'),
]