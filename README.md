# qualityGatePlatform

GitLab质量门禁管理平台

## 快速开始

### 使用 Docker Compose 启动

1. 克隆项目
```bash
git clone <repository-url>
cd qualityGatePlatform
```

2. 启动所有服务
```bash
docker-compose up -d
```

3. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

4. 默认管理员账号
- 用户名: admin
- 密码: Admin@1234

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
```

### 环境变量配置

复制 `.env.example` 为 `.env` 并修改配置:

```bash
cp .env.example .env
```

主要配置项:
- `POSTGRES_PASSWORD`: PostgreSQL 密码
- `JWT_SECRET_KEY`: JWT 密钥 (生产环境必须修改)
- `DEBUG`: 调试模式
- `CORS_ORIGINS`: 允许的跨域来源

## 项目结构

```
qualityGatePlatform/
├── backend/                 # 后端服务
│   ├── app/                # FastAPI 应用
│   ├── alembic/            # 数据库迁移
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile          # 后端容器配置
├── frontend/               # 前端服务
│   ├── dist/               # 构建产物
│   ├── nginx.conf          # Nginx 配置
│   └── Dockerfile          # 前端容器配置
├── nginx/                  # Nginx 反向代理
│   ├── nginx.conf          # 主配置
│   └── ssl/                # SSL 证书
├── docker-compose.yml      # Docker Compose 配置
└── .env                    # 环境变量
```

## 服务架构

- **frontend**: Vue.js 3 + Element Plus (Nginx)
- **backend**: FastAPI + SQLAlchemy (Python 3.11)
- **celery-worker**: Celery 异步任务处理
- **postgres**: PostgreSQL 15 数据库
- **redis**: Redis 7 缓存和消息队列

## 开发模式

### 本地开发 (不使用 Docker)

1. 启动数据库和 Redis
```bash
docker-compose up -d postgres redis
```

2. 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 生产部署

1. 修改 `.env` 文件,设置安全的密码和密钥
2. 取消注释 `docker-compose.yml` 中的 nginx 服务
3. 将 SSL 证书放到 `nginx/ssl/` 目录
4. 启动服务
```bash
docker-compose -f docker-compose.yml up -d
```
