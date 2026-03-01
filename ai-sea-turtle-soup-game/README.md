# AI Sea Turtle Soup Game (AI海龟汤游戏)

> ⚠️ **AI生成声明**：本项目完全由AI生成，包括代码、文档和配置示例。
> 作者：Cline(DeepSeek V3) | 生成时间：2026年2月26日

## 项目简介

这是一个支持多AI玩家参与的**海龟汤游戏**（Sea Turtle Soup Game）。玩家可以与多个AI助手一起玩这个经典的推理游戏，游戏支持传统问答模式和现代猜测模式。

## 功能特点

### 🎮 游戏模式
1. **传统海龟汤模式**：经典的提问-回答模式
   - 猜谜者提问，出题者只能回答"是"、"否"或"无关"
   - 支持"接近"和"可以揭晓"等高级提示
   - 1对1模式或多人轮流提问模式

2. **现代海龟汤模式**：自由猜测模式
   - 猜谜者可以直接提出完整假设
   - 更自由的推理和讨论
   - 适合快速游戏

### 🤖 AI玩家支持
- **多AI集成**：默认支持DeepSeek、ChatGPT、Kimi等AI模型
- **智能对话**：AI会根据游戏上下文进行合理提问和回答
- **赛后聊天**：游戏结束后AI玩家之间会进行自然对话
- **回合聊天**：每回合结束后玩家可以与AI进行小型聊天

### ⚙️ 配置管理
- **交互式配置编辑器**：轻松添加、删除和配置AI玩家
- **系统代理支持**：自动检测和使用系统代理设置
- **游戏设置自定义**：可配置最大轮数、历史记录等
- **配置文件管理**：支持JSON配置文件

### 📊 游戏功能
- **历史记录**：自动保存游戏对话历史
- **赛后复盘**：游戏结束后显示详细统计信息
- **智能超时处理**：API调用超时保护
- **错误友好处理**：网络问题时的优雅降级

## 快速开始

### 环境要求
- Python 3.8+
- requests库

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行游戏
```bash
# 直接运行主游戏
python run.py

# 或运行源代码
python -m src.sea_turtle_soup
```

### 配置AI玩家
1. 首次运行会自动生成配置文件
2. 按照提示输入AI API密钥和配置信息
3. 或手动编辑`configs/config.example.json`文件

## 项目结构

```
AI-SeaTurtleSoup-Game/
├── src/                    # 源代码目录
│   ├── sea_turtle_soup.py # 主游戏逻辑
│   ├── player_manager.py  # 玩家配置管理
│   └── __init__.py        # 包初始化文件
├── configs/               # 配置文件目录
│   ├── config.example.json # 配置文件示例
│   └── README_config.md   # 配置说明文档
├── tests/                 # 测试文件目录
│   ├── test_game.py      # 游戏逻辑测试
│   ├── test_player.py    # 玩家管理测试
│   └── __init__.py       # 测试包初始化
├── examples/              # 使用示例目录
│   └── quick_start.py    # 快速启动示例
├── requirements.txt       # Python依赖列表
├── .gitignore            # Git忽略文件配置
├── README.md             # 本说明文档
└── run.py                # 游戏启动脚本
```

## 详细使用说明

### 游戏启动
运行游戏后，你会看到以下主菜单：

```
====================
    AI海龟汤游戏
====================
当前配置:
  用户角色: 玩家
  AI玩家: DeepSeek, ChatGPT, Kimi
  最大轮数: 10

游戏模式:
1. 传统海龟汤（提问-回答，是/否/无关）
2. 现代海龟汤（自由猜测）

选项:
3. 更改配置
4. 查看历史记录
5. 测试API连接
6. 退出游戏
```

### 游戏玩法

#### 传统海龟汤模式
1. **出题环节**：出题者（人类或AI）提供一个谜题
2. **问答环节**：猜谜者提问，出题者只能用"是"、"否"、"无关"回答
3. **提示机制**：当问题接近真相时，出题者可以回答"接近"
4. **揭晓机制**：当猜谜者基本猜到时，出题者可以回答"可以揭晓"
5. **谜底揭示**：最后揭示完整谜底

#### 现代海龟汤模式
1. **自由出题**：出题者提供完整谜题
2. **自由猜测**：猜谜者直接提出假设和推理
3. **谜底揭示**：最后揭示完整谜底

### 赛后功能
- **回合聊天**：每回合结束后可以与AI进行简短对话
- **赛后复盘**：游戏结束后显示详细统计
- **AI聊天**：AI玩家之间进行赛后交流
- **历史保存**：可选择保存游戏对话到文件

## API密钥配置

### 支持的AI服务
1. **DeepSeek**：`https://api.deepseek.com/v1/chat/completions`
2. **ChatGPT**：`https://api.chatanywhere.tech/v1/chat/completions`
3. **Kimi**：`https://api.moonshot.cn/v1/chat/completions`
4. **其他OpenAI兼容API**：支持任何兼容OpenAI API的服务

### 配置方法
1. **交互式配置**：运行游戏后选择"更改配置"
2. **手动配置**：编辑配置文件`player_config.json`
3. **示例配置**：参考`configs/config.example.json`

### 配置文件示例
```json
{
  "ai_players": [
    {
      "name": "DeepSeek",
      "type": "ai",
      "api_config": {
        "api_key": "your_api_key_here",
        "model": "deepseek-chat",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "temperature": 0.7,
        "use_proxy": true
      }
    }
  ],
  "user_role": "player",
  "game_settings": {
    "max_rounds": 10,
    "enable_history": true,
    "save_conversations": true,
    "auto_detect_proxy": true,
    "proxy_timeout": 30
  }
}
```

## 代理设置

### 自动检测
游戏会自动检测系统代理设置，支持：
- Windows系统代理
- 环境变量 (`HTTP_PROXY`, `HTTPS_PROXY`)
- urllib标准代理检测

### 手动配置
在配置编辑器中选择"配置代理设置"：
1. 使用系统代理（默认）
2. 手动配置代理
3. 禁用代理

### 代理格式
- HTTP代理：`http://proxy.example.com:8080`
- HTTPS代理：`https://proxy.example.com:8080`
- 认证代理：`http://username:password@proxy.example.com:8080`

## 常见问题

### Q: API连接失败怎么办？
A: 尝试以下步骤：
1. 检查网络连接
2. 确认API密钥有效且未过期
3. 检查代理设置是否正确
4. 在游戏菜单中选择"测试API连接"
5. 确认API服务端点URL正确

### Q: 如何添加新的AI服务？
A: 在配置编辑器中：
1. 选择"添加AI玩家"
2. 输入AI名称
3. 输入API密钥
4. 输入模型名称（参考服务商文档）
5. 输入API端点URL
6. 选择是否使用代理

### Q: 游戏历史保存在哪里？
A: 游戏对话历史保存在以下位置：
- 自动保存：`conversation_YYYYMMDD_HHMMSS.json`
- 手动保存：在赛后复盘时选择保存

### Q: 如何修改默认配置？
A: 有以下几种方式：
1. 运行配置编辑器：`python -m src.player_manager`
2. 直接编辑`player_config.json`文件
3. 在游戏主菜单中选择"更改配置"

### Q: 游戏支持哪些语言？
A: 游戏主要支持中文界面和对话，但AI可以处理多种语言。

### Q: API调用会产生费用吗？
A: 是的，使用AI服务可能会产生费用，具体取决于：
- 使用的AI服务提供商
- API调用次数
- 使用的模型类型
- 对话长度和复杂度

## 技术说明

### 依赖项
- `requests>=2.28.0`：用于HTTP请求
- 标准库：json, os, random, sys, time, datetime, typing, urllib

### 代码结构
1. **主游戏类** (`SeaTurtleSoupGame`)：游戏核心逻辑
2. **玩家管理类** (`PlayerConfig`)：配置和代理管理
3. **AI交互模块**：统一的AI API调用接口
4. **游戏历史模块**：对话记录和管理

### 错误处理
- **超时处理**：API调用超时自动跳过
- **代理错误**：代理连接失败时优雅降级
- **API错误**：API返回错误时友好提示
- **配置错误**：配置文件损坏时使用默认配置

### 性能优化
- **上下文限制**：只传递必要的对话历史
- **令牌限制**：限制AI回复长度
- **缓存优化**：代理会话复用
- **异步处理**：未来的改进方向

## 开发说明

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_game.py
python -m pytest tests/test_player.py
```

### 代码规范
- 使用类型提示 (Type Hints)
- 遵循PEP 8编码规范
- 添加详细的文档字符串
- 模块化的代码结构

### 扩展开发
1. **添加新的游戏模式**：继承`SeaTurtleSoupGame`类
2. **集成新的AI服务**：扩展`PlayerConfig`类
3. **改进用户界面**：修改游戏菜单和输出格式
4. **添加新功能**：在适当的模块中添加

## 许可证和安全说明

### 安全注意事项
1. **API密钥保护**：不要将包含真实API密钥的配置文件提交到版本控制
2. **代理安全**：确保代理服务器的安全性
3. **网络通信**：所有API通信使用HTTPS加密
4. **配置文件**：`player_config.json`包含敏感信息，请妥善保管

### 使用建议
1. 使用环境变量存储API密钥
2. 定期更新API密钥
3. 监控API使用情况
4. 使用合适的代理设置

## 更新日志

### v1.0 (2026-02-26)
- 初始版本发布
- 支持多AI玩家
- 传统和现代两种游戏模式
- 系统代理自动检测
- 交互式配置编辑器
- 赛后聊天和复盘功能
- 游戏历史保存功能
- 完整的错误处理和超时保护

### v0.9 (2026-02-25)
- 基础游戏框架
- 单一AI支持
- 基本代理功能
- 配置文件管理

## 贡献和反馈

### 问题报告
如果遇到问题，请检查：
1. Python版本是否为3.8+
2. requests库是否已安装
3. 网络连接是否正常
4. API密钥是否有效

### 功能建议
欢迎提出改进建议：
1. 新的游戏模式
2. 更多的AI集成
3. 用户界面改进
4. 性能优化

## 免责声明

1. 本项目完全由AI生成，可能存在错误或不完善之处
2. 使用AI服务可能产生费用，请用户自行承担
3. 项目开发者不对因使用本项目造成的任何损失负责
4. 请遵守相关AI服务提供商的使用条款

## 开始游戏吧！

准备好与AI一起玩海龟汤游戏了吗？运行以下命令开始：

```bash
python run.py
```

享受推理的乐趣吧！🧠🎮
