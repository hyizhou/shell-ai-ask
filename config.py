#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
负责加载和管理API密钥、模型配置等
"""

import os
import json
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 检查是否处于开发模式（当前目录下存在config.json）
        dev_config_path = os.path.join(os.getcwd(), "config.json")
        is_dev_mode = os.path.exists(dev_config_path)
        
        # 如果处于开发模式且未指定配置路径，则使用当前目录下的config.json
        if is_dev_mode and config_path is None:
            self.config_path = dev_config_path
            print(f"[开发模式] 使用配置文件: {self.config_path}")
        else:
            # 默认配置文件路径
            # 在Windows上使用 %USERPROFILE%\.ai.json
            # 在其他系统上使用 ~/.ai.json
            if os.name == "nt":  # Windows系统
                self.config_path = config_path or os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), ".ai.json")
            else:  # Unix/Linux/MacOS
                self.config_path = config_path or os.path.expanduser("~/.ai.json")
        
        # 默认配置
        self.default_config = {
            "default_model": "openai",
            "models": {
                "openai": {
                    "api_key": "",
                    "model": "gpt-3.5-turbo",
                    "api_base": "https://api.openai.com/v1/"
                },
                "deepseek": {
                    "api_key": "",
                    "model": "deepseek-chat",
                    "api_base": "https://api.deepseek.com/v1/"
                },
                "qwen": {
                    "api_key": "",
                    "model": "qwen-max",
                    "api_base": "https://dashscope.aliyuncs.com/api/v1/"
                }
            },
            "proxy": {
                "enabled": False,
                "http": "",
                "https": ""
            },
            "max_history": 10,  # 保存的最大历史消息数
            "stream_output": True  # 默认启用流式输出
        }
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        如果配置文件不存在，则创建默认配置文件
        
        Returns:
            配置字典
        """
        # 检查配置目录是否存在
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            # 创建默认配置文件
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.default_config, f, indent=4)
            return self.default_config
        
        # 加载现有配置文件
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # 确保配置文件包含所有必要的字段
            for key, value in self.default_config.items():
                if key not in config:
                    config[key] = value
            
            return config
        except Exception as e:
            print(f"警告：无法加载配置文件：{e}")
            return self.default_config
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"警告：无法保存配置文件：{e}")
    
    @property
    def default_model(self) -> str:
        """获取默认模型名称"""
        return self.config.get("default_model", "openai")
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """获取指定模型的配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型配置字典
        """
        models = self.config.get("models", {})
        return models.get(model_name, {})
    
    def set_model_config(self, model_name: str, config: Dict[str, Any]) -> None:
        """设置指定模型的配置
        
        Args:
            model_name: 模型名称
            config: 模型配置字典
        """
        if "models" not in self.config:
            self.config["models"] = {}
        
        self.config["models"][model_name] = config
        self.save_config()
    
    @property
    def max_history(self) -> int:
        """获取最大历史消息数"""
        return self.config.get("max_history", 10)
    
    @property
    def stream_output(self) -> bool:
        """获取是否启用流式输出"""
        return self.config.get("stream_output", True)
    
    @property
    def proxy(self) -> Dict[str, Any]:
        """获取代理配置
        
        Returns:
            代理配置字典，包含enabled, http, https字段
        """
        return self.config.get("proxy", {"enabled": False, "http": "", "https": ""})