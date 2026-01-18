# 教师文档管理系统

一个基于Django的教师文档管理系统，支持分角色权限管理、文档上传下载、版本控制、分享功能等。

## 项目简介

本项目是一个专为教师设计的文档管理系统，旨在帮助教师高效管理教学文档、科研文献等各类文件，支持文档的分类存储、版本控制、权限管理和分享功能，提高文档管理的安全性和便捷性。

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
- **数据库**：MySQL 5.7+ / SQLite
- **前端**：Bootstrap 5 + jQuery
- **任务队列**：Celery + Redis
- **文件存储**：本地文件系统

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ (或使用默认SQLite数据库)
- Redis (可选，用于Celery任务队列)

### 安装部署

1. **克隆项目**
```bash
git clone https://github.com/your-username/teacher-doc-system.git
cd teacher-doc-system/code/teacher_doc_system
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

4. **初始化数据库**
```bash
python setup_database.py
```

5. **启动开发服务器**
```bash
python manage.py runserver
```

6. **访问系统**
- 地址：http://localhost:8000
- 默认管理员账号：admin
- 默认管理员密码：admin123456

## 项目结构

```
software-course/
├── code/
│   └── teacher_doc_system/  # Django项目目录
│       ├── accounts/        # 账户管理应用
│       ├── documents/       # 文档管理应用
│       ├── media/           # 媒体文件存储
│       ├── static/          # 静态文件
│       ├── teacher_doc_system/  # 项目配置
│       ├── manage.py        # Django管理脚本
│       └── requirements.txt # 依赖列表
└── README.md                # 项目说明文档
```

## 详细文档

更多详细信息请查看 [教师文档管理系统详细文档](code/teacher_doc_system/README.md)

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：your-email@example.com
- 项目地址：https://github.com/your-username/teacher-doc-system
