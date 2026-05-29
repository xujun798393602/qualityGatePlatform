# 前端生成报告

## 项目概述

基于后端 API 自动生成的 Vue3 + Element Plus 前端项目。

## 技术栈

- **框架**: Vue 3.4 (Composition API)
- **构建工具**: Vite 5
- **UI 组件库**: Element Plus 2.6
- **状态管理**: Pinia 2
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios 1.6
- **语言**: TypeScript 5.4

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 请求层
│   │   ├── auth.ts       # 认证 API
│   │   ├── users.ts      # 用户 API
│   │   ├── roles.ts      # 角色 API
│   │   ├── teams.ts      # 团队 API
│   │   ├── scripts.ts    # 脚本 API
│   │   ├── repos.ts      # 仓库 API
│   │   ├── pipelines.ts  # 流水线 API
│   │   ├── gates.ts      # 门禁 API
│   │   └── system.ts     # 系统配置 API
│   ├── stores/           # Pinia 状态管理
│   │   └── auth.ts       # 认证状态
│   ├── router/           # 路由配置
│   │   └── index.ts      # 路由 + 权限守卫
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue
│   ├── views/            # 页面组件
│   │   ├── auth/         # 登录、404
│   │   ├── dashboard/    # 仪表盘
│   │   ├── users/        # 用户管理
│   │   ├── roles/        # 角色管理
│   │   ├── teams/        # 团队管理
│   │   ├── scripts/      # 脚本管理
│   │   ├── repos/        # 仓库管理
│   │   ├── pipelines/    # 流水线管理
│   │   ├── gates/        # 门禁管理
│   │   └── system/       # 系统配置
│   ├── utils/            # 工具函数
│   │   └── request.ts    # Axios 封装
│   ├── types/            # TypeScript 类型
│   │   └── index.ts
│   ├── main.ts           # 应用入口
│   └── App.vue           # 根组件
├── package.json
├── vite.config.ts
├── tsconfig.json
└── index.html
```

## 模块说明

### 1. 认证模块
- 登录页面
- JWT Token 存储与自动刷新
- 路由权限守卫
- 退出登录

### 2. 仪表盘
- 统计卡片（用户、角色、团队、脚本、仓库、流水线、门禁）
- 快速操作入口
- 系统信息展示
- 模块概览

### 3. 系统管理
- **用户管理**: 完整 CRUD，支持启用/禁用
- **角色管理**: 完整 CRUD
- **团队管理**: 完整 CRUD

### 4. 质量管理
- **脚本管理**: 管理测试/构建/部署脚本，支持执行
- **仓库管理**: 管理 Git 仓库配置，支持同步
- **流水线管理**: 管理 CI/CD 流水线，支持运行和查看历史
- **门禁管理**: 管理质量门禁规则，支持检查历史

### 5. 系统配置
- 基本配置（系统名称、版本）
- 安全配置（JWT 过期时间、登录尝试限制）
- 调试模式开关

## API 映射

| 模块 | API 文件 | 状态 |
|------|----------|------|
| 认证 | auth.ts | ✅ |
| 用户 | users.ts | ✅ |
| 角色 | roles.ts | ✅ |
| 团队 | teams.ts | ✅ |
| 脚本 | scripts.ts | ✅ |
| 仓库 | repos.ts | ✅ |
| 流水线 | pipelines.ts | ✅ |
| 门禁 | gates.ts | ✅ |
| 系统 | system.ts | ✅ |

## 构建与运行

### 开发模式
```bash
cd frontend
npm install
npm run dev
```

### 生产构建
```bash
cd frontend
npm run build
```

### Docker 构建
```bash
docker compose up -d --build frontend
```

## 访问地址

- 前端: http://localhost:3000
- 后端 API: http://localhost:9000
- API 文档: http://localhost:9000/docs

## 默认账号

- 用户名: admin
- 密码: Admin@1234
