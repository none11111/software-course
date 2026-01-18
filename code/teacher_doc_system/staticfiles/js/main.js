// 主要JavaScript功能

$(document).ready(function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 自动隐藏警告消息
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // 确认删除对话框
    $('.delete-btn, .btn-danger[href*="delete"]').on('click', function(e) {
        if (!confirm('确定要删除吗？此操作不可撤销。')) {
            e.preventDefault();
        }
    });

    // 文件上传拖拽功能
    initFileUpload();
    
    // 搜索功能
    initSearch();
});

// 文件上传功能
function initFileUpload() {
    const dropZone = $('.file-upload-area, .drop-zone');
    
    dropZone.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });
    
    dropZone.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });
    
    dropZone.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        
        const files = e.originalEvent.dataTransfer.files;
        const fileInput = $(this).find('input[type="file"]');
        
        if (fileInput.length > 0 && files.length > 0) {
            fileInput[0].files = files;
            fileInput.trigger('change');
        }
    });
    
    // 文件选择变化（只处理没有特定处理器的文件输入）
    $('input[type="file"]').on('change', function() {
        // 检查是否已经有特定的处理器
        if ($(this).data('has-custom-handler')) {
            return;
        }
        const file = this.files[0];
        if (file) {
            updateFileInfo(file);
        }
    });
}

// 更新文件信息显示
function updateFileInfo(file) {
    const fileInfo = $('.file-info');
    if (fileInfo.length > 0) {
        const fileSize = formatFileSize(file.size);
        const fileType = getFileType(file.name);
        
        fileInfo.html(`
            <div class="d-flex align-items-center">
                <i class="fas fa-file-${getFileIcon(fileType)} me-2"></i>
                <div>
                    <strong>${file.name}</strong><br>
                    <small class="text-muted">${fileSize} • ${fileType.toUpperCase()}</small>
                </div>
            </div>
        `);
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// 获取文件类型
function getFileType(filename) {
    return filename.split('.').pop().toLowerCase();
}

// 获取文件图标
function getFileIcon(fileType) {
    const iconMap = {
        'pdf': 'pdf',
        'doc': 'word',
        'docx': 'word',
        'ppt': 'powerpoint',
        'pptx': 'powerpoint',
        'xls': 'excel',
        'xlsx': 'excel',
        'txt': 'alt',
        'md': 'alt',
        'zip': 'archive',
        'rar': 'archive',
        '7z': 'archive',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image'
    };
    
    return iconMap[fileType] || 'alt';
}

// 搜索功能
function initSearch() {
    const searchInput = $('input[name="search"]');
    
    if (searchInput.length > 0) {
        // 实时搜索（防抖）
        let searchTimeout;
        searchInput.on('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                const query = searchInput.val();
                if (query.length > 2) {
                    // 这里可以添加AJAX搜索功能
                    console.log('搜索:', query);
                }
            }, 300);
        });
        
        // 回车搜索
        searchInput.on('keypress', function(e) {
            if (e.which === 13) {
                $(this).closest('form').submit();
            }
        });
    }
}