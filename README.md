# 航空公司产品智能体 (Air PRD Agent)

> 基于 LangGraph + FastAPI 的航空公司产品查询智能体系统

## 项目简介

本项目是一个独立的航空公司产品智能体系统，基于 main.py 作为主入口文件构建。该系统提供产品查询、搜索、统计等功能，支持通过 Web 界面和 API 调用。

## 目录结构

```
air_prd_agent/
├── src/                    # 源代码目录
│   ├── main.py             # 主入口文件
│   ├── agents/             # 智能体模块
│   │   └── agent.py        # 航空公司产品智能体
│   ├── graphs/             # LangGraph 图定义
│   │   └── nodes/          # 图节点
│   ├── utils/              # 工具模块
│   │   ├── airline_names.py    # 航司名称映射
│   │   ├── file_parser.py      # 文件解析
│   │   └── file/               # 文件处理工具
│   ├── storage/            # 存储模块
│   │   ├── database/       # 数据库
│   │   ├── memory/         # 内存存储
│   │   └── s3/             # S3存储
│   └── tools/             # 工具集
├── static/                # 前端静态文件
│   ├── index.html          # 主页面
│   └── ...                 # 其他静态资源
├── config/                 # 配置文件
│   └── agent_llm_config.json  # LLM配置
├── assets/                 # 数据和文档
│   ├── products.csv        # 产品数据
│   ├── docs/               # 帮助文档
│   └── ...
├── 快速启动.bat            # 快速启动服务
├── 重启服务.bat            # 重启服务
├── 停止服务.bat            # 停止服务
├── 检查服务状态.bat        # 检查服务状态
└── 后台启动服务.bat        # 后台启动服务
```

## 快速开始

### 环境要求

- Python 3.12+
- Windows 系统

### 启动服务

双击运行 `快速启动.bat` 即可启动服务。

服务启动后访问：
- 本地: http://localhost:8000
- 局域网: http://192.168.101.2:8000

### 主要功能

1. **产品查询** - 根据航空公司代码查询产品
2. **产品搜索** - 支持关键词搜索
3. **票证类型筛选** - 按 GP/BSP/B2B 类型筛选
4. **统计信息** - 查看产品统计数据
5. **文件上传** - 支持 CSV/Excel 产品数据导入

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/run` | POST | 执行智能体 |
| `/stream_run` | POST | 流式执行 |
| `/api/airlines` | GET | 获取航司列表 |
| `/api/airlines/{code}` | GET | 获取航司产品 |
| `/api/search` | GET | 搜索产品 |
| `/api/stats` | GET | 统计信息 |
| `/api/upload/file` | POST | 上传文件 |
| `/health` | GET | 健康检查 |

## 启动脚本说明

| 脚本 | 说明 |
|------|------|
| 快速启动.bat | 交互式启动服务 |
| 重启服务.bat | 重启服务并打开浏览器 |
| 停止服务.bat | 停止服务 |
| 检查服务状态.bat | 查看服务运行状态 |
| 后台启动服务.bat | 后台静默启动服务 |
| 同步项目文件.bat | 首次设置时同步源代码和配置文件 |

## 首次设置

首次使用前，请运行 `同步项目文件.bat` 来复制源代码、静态文件和配置文件到本项目。

## 注意事项

1. 本项目为独立项目，与原 release_20260317_100737 目录分离
2. 核心文件(main.py, agent.py)已创建，其他文件请通过"同步项目文件.bat"复制
3. 如需更新数据，请修改 assets/products.csv 文件
4. 服务默认端口为 8000

## 技术栈

- **后端**: FastAPI + LangGraph + LangChain
- **LLM**: 字节豆包模型 (doubao-seed-1-6-251015)
- **前端**: HTML + JavaScript

---
*创建时间: 2026-03-19*
