#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话管理模块
负责处理用户与AI之间的对话
"""

import sys
from typing import List, Dict, Any, Optional, Union, Generator

from models import BaseModel


class Conversation:
    """对话管理类"""
    
    def __init__(self, model: BaseModel, max_history: int = 10):
        """初始化对话
        
        Args:
            model: 模型实例
            max_history: 最大历史消息数
        """
        self.model = model
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到历史记录
        
        Args:
            role: 消息角色（"user"或"assistant"）
            content: 消息内容
        """
        self.messages.append({"role": role, "content": content})
        
        # 如果历史记录超过最大限制，删除最早的消息
        # 保留system消息（如果有）
        if len(self.messages) > self.max_history:
            # 检查第一条消息是否是system消息
            if self.messages and self.messages[0]["role"] == "system":
                # 保留system消息，删除最早的用户或助手消息
                self.messages = [self.messages[0]] + self.messages[-(self.max_history-1):]
            else:
                # 没有system消息，直接保留最近的max_history条消息
                self.messages = self.messages[-self.max_history:]
    
    def send_message(self, message: str, stream: bool = True) -> Union[str, None]:
        """发送消息并获取回复
        
        Args:
            message: 用户消息
            stream: 是否使用流式输出
            
        Returns:
            如果stream为False，返回完整的回复字符串
            如果stream为True，直接打印流式输出，返回None
        """
        # 添加用户消息到历史记录
        self.add_message("user", message)
        
        # 生成回复
        if stream:
            # 流式输出
            response_text = ""
            for chunk in self.model.generate(self.messages, stream=True):
                sys.stdout.write(chunk)
                sys.stdout.flush()
                response_text += chunk
            
            # 添加助手回复到历史记录
            self.add_message("assistant", response_text)
            return None
        else:
            # 非流式输出
            response_text = self.model.generate(self.messages, stream=False)
            
            # 添加助手回复到历史记录
            self.add_message("assistant", response_text)
            return response_text
    
    def clear_history(self) -> None:
        """清空对话历史"""
        # 保留system消息（如果有）
        if self.messages and self.messages[0]["role"] == "system":
            self.messages = [self.messages[0]]
        else:
            self.messages = []
    
    def set_system_message(self, content: str) -> None:
        """设置系统消息
        
        Args:
            content: 系统消息内容
        """
        # 检查是否已有system消息
        if self.messages and self.messages[0]["role"] == "system":
            # 更新现有system消息
            self.messages[0]["content"] = content
        else:
            # 添加新的system消息到最前面
            self.messages.insert(0, {"role": "system", "content": content})