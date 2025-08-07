# ShellAIAsk: 轻量级命令行AI助手工具

ShellAIAsk是一个轻量级命令行AI助手工具，允许用户在终端直接与各大语言模型进行交互，无需切换至浏览器，提高工作效率。

## 功能特点

- **命令触发**：通过`ask [query]`命令启动AI对话
- **持续对话模式**：命令执行后进入交互式对话界面
- **管道支持**：支持通过管道输入文本，并触发AI对话
- **多模型支持**：支持OpenAI、DeepSeek、通义千问等多种模型API
- **流式输出**：实时显示AI回复，提升用户体验
- **极简依赖**：仅依赖 requests

## 安装方法

### 从源码安装

#### 使用 uv（推荐）

```bash
# 克隆仓库
git clone https://github.com/hyizhou/shell-ai-ask.git
cd shell-ai-ask

# 使用 uv 安装
uv tool install .
```

#### 使用 pip

```bash
# 克隆仓库
git clone https://github.com/hyizhou/shell-ai-ask.git
cd shell-ai-ask

# 使用 pip 安装
pip install .
```

### 依赖项

本工具依赖以下Python库：
- requests>=2.25.0
- pyreadline3>=3.4.0 (仅Windows平台)

## 配置

### 环境配置

首次运行时，程序会在用户主目录下创建配置文件：
- Windows系统：`%USERPROFILE%\.ai.json`
- 其他系统：`~/.ai.json`

您需要编辑此文件，添加您的API密钥：

```json
{
    "default_model": "openai",
    "models": {
        "openai": {
            "api_key": "your-openai-api-key",
            "model": "gpt-3.5-turbo",
            "api_base": "https://api.openai.com/v1/"
        },
        "deepseek": {
            "api_key": "your-deepseek-api-key",
            "model": "deepseek-chat",
            "api_base": "https://api.deepseek.com/v1/"
        },
        "qwen": {
            "api_key": "your-qwen-api-key",
            "model": "qwen-max",
            "api_base": "https://dashscope.aliyuncs.com/api/v1/"
        }
    },
    "proxy": {
        "enabled": false,
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
    "max_history": 10,
    "stream_output": true,
    "language": "auto"  // 界面语言：auto(自动检测)|zh(中文)|en(英文)
}
```

您也可以通过环境变量设置API密钥：

```bash
export OPENAI_API_KEY="your-openai-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QWEN_API_KEY="your-qwen-api-key"
```


### 开发环境配置

在开发过程中，如果当前工作目录下存在`config.json`文件，程序会优先使用该配置文件，而不是用户主目录下的配置文件。

开发模式下，程序会显示以下提示信息：

```
[开发模式] 使用配置文件: /path/to/current/directory/config.json
```

当您完成开发并安装到系统后，程序将自动切换回使用用户主目录下的配置文件。

## 使用方法

### 基本用法

```bash
# 直接提问，可多轮对话
ask 如何查看Linux磁盘使用情况？

# 指定模型
ask -m deepseek 如何优化Python代码性能？

# 禁用流式输出
ask --no-stream 请解释Docker的工作原理

# 仅进行一次对话，回答后立即退出
ask --once 什么是Python装饰器

# 显示版本信息
ask -v

# 显示帮助信息（包含配置文件位置）
ask -h
```

### 交互模式

执行`ask`命令后，默认会进入交互模式，您可以连续提问：

使用`--once`参数避免进入交互模式。

```
$ ask
进入交互模式。输入'exit'或'quit'或按Ctrl+C退出。
> 什么是机器学习？
[AI回复...]

> 它与深度学习有什么区别？
[AI回复...]

> exit
再见！
```

### 管道支持

ShellAIAsk 支持从管道接收输入，这对于处理其他命令的输出非常有用：

```
# 分析命令输出
ls -la | ask "请解释这个目录结构"

# 分析文件内容
cat error.log | ask "这个日志有什么问题？"

# 分析代码
cat main.py | ask "这段代码有什么可以优化的地方？"

# 管道输入后立即退出（一次性处理）
echo "Hello World" | ask "翻译成中文" --once 
```