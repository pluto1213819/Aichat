# 🤖 AI Chat - 智能即时通讯系统

<p align="center">
  <strong>基于 Socket + 多线程的 PC 端智能即时通讯系统，集成 AI Agent 智能体，实现智能应答与辅助沟通</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Socket-多线程-green" alt="Socket">
  <img src="https://img.shields.io/badge/PyQt5-GUI-purple" alt="PyQt5">
  <img src="https://img.shields.io/badge/AI-Agent-智能体-red" alt="AI Agent">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## 📋 项目概述

AI Chat 是一款专为局域网环境设计的智能即时通讯软件，采用经典的客户端-服务器架构模式。系统基于 **Python Socket + 多线程** 搭建高并发通讯服务，落地账号体系、单/群聊、实时消息、文件传输、好友管理等核心模块，并集成 **AI Agent 智能体**，实现智能应答、内容解析、智能辅助沟通等功能，打通传统通讯与 AI 智能交互的能力链路。

## ✨ 核心特性

### 📡 高并发通讯架构
- 基于 TCP Socket 的持久连接，JSON 协议数据交换
- 多线程并发处理，支持 100+ 并发用户连接
- 心跳检测机制，自动断线重连
- 离线消息存储，上线自动推送

### 👥 完整账号体系
- 用户注册 / 登录，数学验证码安全验证
- 密码找回（安全问题验证）
- 会话管理，单设备登录限制
- 个人资料管理（头像、昵称、签名）

### 💬 单聊 & 群聊
- 实时文字消息收发，消息气泡 UI
- 群组创建 / 加入 / 退出 / 解散
- 群主管理权限（踢人、邀请）
- 聊天记录持久化存储

### 📎 文件传输
- 文件发送 / 接收，带确认机制
- 传输进度反馈
- 断点续传支持

### 👫 好友管理
- 用户名搜索添加好友
- 好友申请 / 接受 / 拒绝
- 好友列表实时在线状态显示
- 右键菜单：发送消息、删除好友

### 🤖 AI Agent 智能体（NEW）

| 功能 | 说明 |
|------|------|
| **AI 智能对话** | 与 AI 助手自由对话，支持上下文记忆 |
| **自动应答** | 用户离线/暂离时，AI 代为自动回复 |
| **内容摘要** | 对长文本进行智能摘要，提取关键信息 |
| **智能翻译** | 支持中英文等多语言互译 |
| **文本润色** | AI 辅助优化文字表达，使其更通顺专业 |
| **情感分析** | 分析文本的情感倾向（积极/消极/中性） |
| **智能建议回复** | 根据聊天上下文推荐合适的回复内容 |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    客户端 (PyQt5 GUI)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ 登录注册  │ │ 好友管理  │ │ 单聊/群聊 │ │ AI 智能助手 │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘  │
│       └────────────┴────────────┴─────────────┘          │
│                        │ Socket TCP                      │
└────────────────────────┼────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────┐
│                    服务端 (多线程)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ 网络服务  │ │ 数据库    │ │ AI Agent │ │ 管理界面   │  │
│  │ (Socket) │ │ (SQLite) │ │  智能体  │ │  (PyQt5)  │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              AI Agent 智能体模块                      │ │
│  │  ┌───────────┐ ┌───────────┐ ┌──────────────────┐  │ │
│  │  │ AgentCore │ │SmartReply │ │ ContentAnalyzer  │  │ │
│  │  │  对话引擎  │ │ 智能回复  │ │   内容解析器     │  │ │
│  │  └─────┬─────┘ └─────┬─────┘ └────────┬─────────┘  │ │
│  │        └──────────────┴────────────────┘            │ │
│  │  ┌──────────────────────────────────────────────┐   │ │
│  │  │          LLM Adapter 适配层                   │   │ │
│  │  │  ┌────────┐ ┌────────┐ ┌────────────────┐   │   │ │
│  │  │  │ OpenAI │ │DeepSeek│ │  MockAdapter   │   │   │ │
│  │  │  │Adapter │ │Adapter │ │  (本地模拟)     │   │   │ │
│  │  │  └────────┘ └────────┘ └────────────────┘   │   │ │
│  │  └──────────────────────────────────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────┐   │ │
│  │  │       AutoResponder 自动应答引擎              │   │ │
│  │  │  用户级开关 · 黑白名单 · 冷却时间控制         │   │ │
│  │  └──────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
Aichat/
├── 客户端/                          # 客户端代码
│   ├── client.py                    # 客户端主程序入口
│   ├── client_network.py            # 网络通信模块
│   ├── client_ui_new.py             # 用户界面模块
│   ├── friend_request_manager.py    # 好友请求管理
│   ├── config.json                  # 客户端配置
│   ├── requirements.txt             # 依赖包
│   ├── m.webp                       # 默认男性头像
│   └── w.webp                       # 默认女性头像
│
├── 服务端/                          # 服务端代码
│   ├── server.py                    # 服务端主程序入口
│   ├── network_server.py            # 网络服务模块
│   ├── server_ui.py                 # 服务端管理界面
│   ├── user_ui.py                   # 用户管理界面
│   ├── database.py                  # 数据库操作模块
│   ├── ai_config.json               # AI Agent 配置
│   ├── ai_agent/                    # AI Agent 智能体模块
│   │   ├── __init__.py
│   │   ├── agent_core.py            # Agent 核心引擎
│   │   ├── llm_adapter.py           # LLM 适配层
│   │   ├── smart_reply.py           # 智能回复建议
│   │   ├── content_analyzer.py      # 内容解析引擎
│   │   └── auto_responder.py        # 自动应答引擎
│   └── config.json                  # 服务端配置
│
├── .gitignore
├── README.md
└── LICENSE
```

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| **GUI** | PyQt5 |
| **数据库** | SQLite3 |
| **网络通信** | Python Socket + 多线程 |
| **数据格式** | JSON |
| **AI 对接** | OpenAI / DeepSeek / 本地大模型（适配器模式） |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 7+ / macOS 10.12+ / Linux

### 安装依赖

```bash
# 客户端
cd 客户端
pip install -r requirements.txt

# 服务端
cd 服务端
pip install PyQt5>=5.15.0
```

### 启动服务

```bash
# 1. 先启动服务端
cd 服务端
python server.py

# 2. 再启动客户端
cd 客户端
python client.py
```

### 配置 AI Agent（可选）

编辑 `服务端/ai_config.json`：

```json
{
  "enabled": true,
  "provider": "openai",
  "api_key": "sk-your-api-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo"
}
```

支持的 AI 提供商：

| Provider | 说明 |
|----------|------|
| `mock` | 本地模拟（默认，无需 API Key） |
| `openai` | OpenAI API |
| `deepseek` | DeepSeek API |
| 自定义 | 任何 OpenAI 兼容接口 |

## 📡 通信协议

客户端与服务端通过 JSON 格式进行数据交换，核心消息类型：

| 类型 | 方向 | 说明 |
|------|------|------|
| `auth` | C→S | 登录认证 |
| `register` | C→S | 用户注册 |
| `chat` | C↔S | 单聊消息 |
| `group_chat` | C↔S | 群聊消息 |
| `add_friend` | C→S | 添加好友 |
| `delete_friend` | C→S | 删除好友 |
| `file_transfer_request` | C→S | 文件传输请求 |
| `ai_chat` | C→S | AI 对话请求 |
| `ai_summarize` | C→S | AI 摘要请求 |
| `ai_translate` | C→S | AI 翻译请求 |

## 📊 数据库设计

| 表名 | 说明 |
|------|------|
| `users` | 用户信息表 |
| `friends` | 好友关系表 |
| `groups` | 群组表 |
| `group_members` | 群成员表 |
| `messages` | 消息记录表 |
| `offline_messages` | 离线消息表 |
| `sessions` | 会话表 |
| `ai_conversations` | AI 对话历史表 |
| `ai_settings` | AI 用户配置表 |

## 🤖 AI Agent 架构

AI Agent 采用模块化设计，支持热更新配置：

- **AgentCore**：对话上下文管理，多轮对话支持
- **LLMAdapter**：统一接口适配 OpenAI / DeepSeek / 本地模型
- **SmartReplyEngine**：基于规则 + LLM 的双模式智能回复
- **ContentAnalyzer**：文本摘要、翻译、润色、情感分析
- **AutoResponder**：用户离线时自动应答，支持黑白名单

## 📝 更新日志

### v2.0.0 (2026-05)
- ✨ 集成 AI Agent 智能体模块
- ✨ 新增智能对话、自动应答、内容解析功能
- ✨ 新增群组管理（创建/解散/踢人/邀请）
- ✨ 新增好友删除、右键菜单操作
- ✨ 侧边栏好友/群组双标签页
- 🔧 优化消息处理机制，支持更多消息类型
- 🔧 优化 UI 交互体验

### v1.0.0 (2025-12)
- 🎉 项目初始化
- ✅ 用户注册/登录系统
- ✅ 好友管理（搜索/添加/接受/拒绝）
- ✅ 单聊/群聊功能
- ✅ 文件传输功能
- ✅ 离线消息存储
- ✅ 服务端管理界面

## 📄 License

MIT License

## 👨‍💻 作者

**pluto1213819** - [GitHub](https://github.com/pluto1213819)
