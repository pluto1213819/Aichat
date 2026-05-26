# Nova Chatting

基于 PyQt5 和 Socket 的局域网即时通讯系统，支持用户注册登录、好友管理、实时聊天、群组通信等功能。

## 功能特性

- **用户系统** — 注册、登录、密码找回、个人资料编辑、头像自定义
- **好友管理** — 搜索用户、发送/接受/拒绝好友请求、好友列表
- **即时通讯** — 一对一私聊、群组聊天、离线消息存储与推送
- **文件传输** — 支持文件发送与接收
- **安全机制** — 密码哈希存储（bcrypt）、验证码校验、账号锁定策略
- **服务端管理** — 在线用户监控、用户管理（增删改查）、系统状态面板、实时日志
- **状态显示** — 用户在线/离线状态实时更新

## 技术栈

| 层级 | 技术 |
|------|------|
| GUI 框架 | PyQt5 >= 5.15.0 |
| 网络通信 | Python Socket + 自定义帧协议（4字节长度头 + JSON） |
| 数据存储 | SQLite3 |
| 密码加密 | bcrypt / hashlib |
| 数据格式 | JSON |
| 并发模型 | threading 多线程 |

## 目录结构

```
Wechat/
├── 客户端/                        # 客户端代码
│   ├── client.py                 # 客户端入口
│   ├── client_network.py         # 网络通信模块
│   ├── client_ui_new.py          # 主界面（登录/聊天）
│   ├── friend_request_manager.py # 好友请求管理窗口
│   ├── config.json               # 客户端配置
│   ├── requirements.txt          # Python 依赖
│   ├── m.webp / w.webp           # 默认头像（男/女）
│   └── cons/                     # 图标资源
│
├── 服务端/                        # 服务端代码
│   ├── server.py                 # 服务端入口
│   ├── network_server.py         # 网络服务与客户端线程管理
│   ├── server_ui.py              # 服务端管理界面
│   ├── user_ui.py                # 用户管理界面
│   ├── database.py               # 数据库操作模块
│   ├── config.json               # 服务端配置
│   └── requirements.txt          # Python 依赖
│
└── README.md
```

## 环境要求

- Python 3.8+
- 操作系统：Windows / macOS / Linux

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/pluto1213819/Wechat.git
cd Wechat
```

### 2. 安装依赖

**客户端：**
```bash
cd 客户端
pip install -r requirements.txt
```

**服务端：**
```bash
cd 服务端
pip install -r requirements.txt
```

### 3. 启动程序

**先启动服务端：**
```bash
cd 服务端
python server.py
```

**再启动客户端：**
```bash
cd 客户端
python client.py
```

> **注意：** 必须先启动服务端，客户端才能正常连接。默认监听地址 `127.0.0.1:8000`。

## 配置说明

### 客户端配置 (`客户端/config.json`)

```json
{
  "server": { "host": "127.0.0.1", "port": 8000 },
  "user": { "username": "", "remember_password": false, "auto_login": false },
  "chat": { "font_size": 12, "font_family": "Microsoft YaHei UI", "show_timestamp": true }
}
```

### 服务端配置 (`服务端/config.json`)

```json
{
  "server": { "host": "127.0.0.1", "port": 8000, "max_connections": 100 },
  "database": { "path": "im_database.db", "backup_enabled": true, "backup_interval_hours": 24 },
  "security": { "password_min_length": 6, "max_login_attempts": 5, "lock_duration_hours": 24 },
  "avatars": { "max_size_mb": 2, "allowed_formats": ["png", "jpg", "jpeg", "gif"] },
  "logging": { "level": "INFO", "max_files": 10, "max_size_mb": 10 }
}
```

## 使用说明

### 服务端

1. 启动后显示管理控制台，可查看在线用户和系统状态
2. 支持用户的增删改查和锁定/解锁操作
3. 实时日志面板记录所有网络事件
4. 可配置服务器端口、心跳间隔等参数

### 客户端

1. 启动后进入登录界面，新用户点击"注册账号"
2. 登录后可添加好友、查看好友列表、收发消息
3. 支持修改个人信息和自定义头像
4. 支持群组聊天和文件传输

## License

MIT License

## Author

pluto1213819
