#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
shell-ai-ask: 轻量级命令行AI助手工具
允许用户在终端直接与各大语言模型进行交互
"""

import argparse
import os
import sys
import signal
from typing import List, Optional
import platform

# 根据操作系统初始化readline
if platform.system() == 'Windows':
    try:
        import pyreadline3
    except ImportError:
        from i18n import t
        print(t("warning_pyreadline_not_installed"))
else:
    try:
        import readline
    except ImportError:
        from i18n import t
        print(t("warning_readline_not_found"))

from .config import Config
from .models import get_model_instance
from .conversation import Conversation
from .i18n import init_i18n, t


def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    print(f"\n{t('goodbye')}")
    sys.exit(0)


def reopen_stdin():
    """重新打开stdin以支持交互输入"""
    try:
        if platform.system() == 'Windows':
            # Windows下重新打开stdin
            sys.stdin = open('CON', 'r')
        else:
            # Unix/Linux下重新打开stdin
            sys.stdin = open('/dev/tty', 'r')
        return True
    except Exception as e:
        print(t("error_cannot_reopen_stdin").format(error=e))
        return False


def main():
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 获取配置文件路径
    config = Config()
    
    # 初始化国际化
    init_i18n(config.language if config.language != "auto" else None)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description=f"{t('app_name')}: {t('app_description')}",
        epilog=t("config_file_location").format(path=os.path.abspath(config.config_path))
    )
    parser.add_argument(
        "query", nargs="*", default=[],
        help=t("help_query")
    )
    parser.add_argument(
        "-m", "--model", type=str, default=None,
        help=t("help_model")
    )
    parser.add_argument(
        "--no-stream", action="store_true",
        help=t("help_no_stream")
    )
    parser.add_argument(
        "--once", action="store_true",
        help=t("help_once")
    )
    parser.add_argument(
        "-v", "--version", action="store_true",
        help=t("help_version")
    )
    
    args = parser.parse_args()
    
    # 显示版本信息
    if args.version:
        try:
            # 尝试使用 importlib.metadata (Python 3.8+) 或 pkg_resources
            try:
                from importlib.metadata import version
                app_version = version("shell-ai-ask")
            except ImportError:
                # 回退到 pkg_resources (Python < 3.8)
                import pkg_resources
                app_version = pkg_resources.get_distribution("shell-ai-ask").version
            print(t("version_info").format(app_name=t("app_name"), version=app_version))
        except Exception as e:
            print(t("warning_version_not_found").format(error=e))
        sys.exit(0)
    
    # 检测并读取管道输入
    stdin_content = ""
    has_pipe_input = not sys.stdin.isatty()
    if has_pipe_input:  # 检测是否有管道输入
        try:
            stdin_content = sys.stdin.read().strip()
            # 读取完管道输入后，重新打开stdin以支持交互模式
            if not args.once:  # 如果不是一次性模式，重新打开stdin
                if not reopen_stdin():
                    print(t("error_cannot_reopen_stdin").format(error="无法重新打开stdin"))
                    has_pipe_input = True  # 强制退出
                else:
                    has_pipe_input = False  # 重新打开成功，可以进入交互模式
        except KeyboardInterrupt:
            sys.exit(0)
    
    # 确定要使用的模型
    model_name = args.model or config.default_model
    model = get_model_instance(model_name, config)
    
    if not model:
        print(t("error_model_load_failed").format(model=model_name))
        sys.exit(1)
    
    # 创建对话实例
    conversation = Conversation(model)
    
    # 构建完整的查询内容
    query_parts = []
    if stdin_content:  # 如果有管道输入，添加到查询中
        query_parts.append(t("stdin_content_prefix").format(content=stdin_content))
    if args.query:  # 如果有命令行参数，添加到查询中
        query_parts.extend(args.query)
    
    initial_query = " ".join(query_parts) if query_parts else ""
    
    # 处理初始查询（如果有）
    if initial_query:
        response = conversation.send_message(initial_query, stream=not args.no_stream)
        if not args.no_stream:
            # 流式输出已经在send_message中处理
            print("\n")
        else:
            print(f"\n{response}\n")
        
        # 如果指定了--once参数，回答后立即退出
        if args.once:
            sys.exit(0)
    elif args.once:
        # 如果指定了--once参数但没有初始查询，提示用户并退出
        print(t("error_once_mode_no_query"))
        sys.exit(1)
    
    # 如果有管道输入但重新打开stdin失败，退出
    if has_pipe_input:
        sys.exit(0)
    
    # 进入交互模式
    print(t("notice_interactive_mode"))
    while True:
        try:
            user_input = input(t("prompt_user_input"))
            if user_input.lower() in ["exit", "quit"]:
                print(t("goodbye"))
                break
                
            response = conversation.send_message(user_input, stream=not args.no_stream)
            if not args.no_stream:
                # 流式输出已经在send_message中处理
                print("\n")
            else:
                print(f"\n{response}\n")
                
        except KeyboardInterrupt:  # 处理Ctrl+C
            print(f"\n{t('goodbye')}")
            break


if __name__ == "__main__":
    main()