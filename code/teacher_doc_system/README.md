# 教师文档管理系统

一个基于Django的教师文档管理系统，支持分角色权限管理、文档上传下载、版本控制、分享功能等。

## 功能特性

### 🔐 用户管理
- **双角色系统**：教师和管理员角色分离
- **统一登录**：支持工号和用户名登录
- **权限控制**：严格的权限边界，防止越界访问
- **账户管理**：冻结/解冻、密码重置、批量导入

### 📁 文档管理
- **文档上传**：支持多种文件格式，自动类型识别
- **版本控制**：文档版本管理，支持回退和对比
- **分类标签**：灵活的文档分类和标签系统
- **搜索筛选**：强大的搜索和筛选功能

### 🔗 分享功能
- **分享链接**：生成限时分享链接
- **访问控制**：支持密码保护和下载次数限制
- **分享记录**：完整的分享历史记录

### 📊 系统管理
- **仪表盘**：系统概览和统计数据
- **用户管理**：用户增删改查、批量导入导出
- **系统配置**：存储配额、分享设置等配置
- **备份恢复**：数据备份和恢复功能
- **操作日志**：完整的审计日志记录

## 技术栈

- **后端**：Django 4.2 + Python 3.8+
- **数据库**：MySQL 5.7+
- **前端**：Bootstrap 5 + jQuery
- **任务队列**：Celery + Redis
- **文件存储**：本地文件系统

## 安装部署

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Redis (可选，用于Celery任务队列)

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd teacher_doc_system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，配置数据库等信息
```

4. **启动系统**
```bash
chmod +x run.sh
./run.sh
```

5. **访问系统**
- 访问地址：http://localhost:8000
- 管理员账号：admin
- 管理员密码：admin123456

### 手动安装

1. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE teacher_doc_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 配置 .env 文件
DB_NAME=teacher_doc_system
DB_USER=root
DB_PASSWORD=your_password
```

4. **初始化数据库**
```bash
python setup_database.py
```

5. **启动开发服务器**
```bash
python manage.py runserver
```

## 配置说明

### 环境变量配置

创建 `.env` 文件并配置以下参数：

```env
# Django配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=teacher_doc_system
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# 文件上传配置
MAX_FILE_SIZE=2147483648  # 2GB
DEFAULT_STORAGE_QUOTA=10737418240  # 10GB
SHARE_LINK_EXPIRY_DAYS=7
```

### 系统配置

管理员可以通过系统配置页面设置：
- 默认存储配额
- 文件上传限制
- 分享链接有效期
- 密码策略
- 备份策略

## 使用指南

### 管理员功能

1. **用户管理**
   - 添加新用户（教师/管理员）
   - 批量导入用户（CSV格式）
   - 冻结/解冻用户账户
   - 重置用户密码

2. **系统配置**
   - 存储配额设置
   - 分享链接配置
   - 安全策略设置
   - 备份策略配置

3. **数据备份**
   - 手动创建备份
   - 自动备份设置
   - 备份文件下载
   - 数据恢复

4. **日志审计**
   - 用户操作日志
   - 系统事件日志
   - 登录记录查看

### 教师功能

1. **文档管理**
   - 上传文档（支持拖拽）
   - 编辑文档信息
   - 文档分类管理
   - 文档搜索筛选

2. **版本控制**
   - 文档版本管理
   - 版本对比
   - 版本回退
   - 更新日志记录

3. **分享功能**
   - 创建分享链接
   - 设置访问密码
   - 限制下载次数
   - 查看分享记录

4. **个人中心**
   - 个人信息管理
   - 密码修改
   - 登录记录查看
   - 存储使用情况

## API接口

系统提供RESTful API接口：

- `GET /api/stats/` - 获取系统统计信息
- `GET /api/user-stats/` - 获取用户统计信息
- `GET /api/document-info/<id>/` - 获取文档信息
- `POST /api/upload-progress/` - 上传进度查询

## 安全特性

- **权限控制**：基于角色的访问控制（RBAC）
- **数据验证**：严格的文件类型和大小验证
- **操作审计**：完整的操作日志记录
- **密码策略**：强制密码复杂度要求
- **会话管理**：安全的会话控制

## 性能优化

- **文件去重**：基于MD5哈希的文件去重
- **分页查询**：大数据量分页显示
- **缓存机制**：Redis缓存提升性能
- **异步任务**：Celery处理耗时任务

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确认数据库用户权限

2. **文件上传失败**
   - 检查文件大小是否超限
   - 验证文件类型是否支持
   - 确认存储空间是否充足

3. **权限访问错误**
   - 确认用户角色设置
   - 检查权限中间件配置
   - 验证URL路由配置

### 日志查看

```bash
# 查看Django日志
tail -f logs/django.log

# 查看Celery日志
tail -f logs/celery.log

# 查看系统日志
tail -f logs/system.log
```

## 开发指南

### 项目结构

```
teacher_doc_system/
├── teacher_doc_system/     # Django项目配置
├── users/                  # 用户管理应用
├── documents/              # 文档管理应用
├── system/                 # 系统管理应用
├── templates/              # 模板文件
├── static/                 # 静态文件
├── media/                  # 媒体文件
├── logs/                   # 日志文件
└── requirements.txt        # 依赖包列表
```

### 添加新功能

1. 在相应的应用中创建模型
2. 编写视图和表单
3. 配置URL路由
4. 创建模板文件
5. 添加权限控制
6. 编写测试用例

### 数据库迁移

```bash
# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations
```

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：your-email@example.com
- 项目地址：https://github.com/your-username/teacher_doc_system

---

**注意**：首次使用请务必修改默认管理员密码，并配置合适的系统参数。
