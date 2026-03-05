# OpenClaw Studio Frontend

OpenClaw Studio 前端应用，使用 React + TypeScript + Vite 构建。

## 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design** - UI 组件库
- **TanStack Query** - 数据获取和缓存
- **Zustand** - 状态管理
- **React Router** - 路由管理

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 环境变量

创建 `.env` 文件并配置：

```
VITE_API_BASE_URL=http://localhost:8000
```

## 项目结构

```
src/
├── components/          # 通用组件
├── features/            # 功能模块
│   ├── requirement-center/  # 需求中心
│   ├── planning/            # 规划视图
│   ├── execution/           # 执行视图
│   ├── testing/             # 测试视图
│   └── history/            # 历史视图
├── services/            # API 服务
├── store/               # 状态管理
├── utils/               # 工具函数
├── App.tsx              # 主应用组件
└── main.tsx             # 入口文件
```
