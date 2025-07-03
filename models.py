#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型接口模块
负责与不同的AI模型API进行交互
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Generator, Union, Callable

import requests
from config import Config


class BaseModel(ABC):
    """模型基类，定义了所有模型必须实现的接口"""
    
    def __init__(self, config: Dict[str, Any], proxy_config: Dict[str, Any] = None):
        """初始化模型
        
        Args:
            config: 模型配置字典
            proxy_config: 代理配置字典
        """
        self.config = config
        self.api_key = config.get("api_key", "")
        self.model_name = config.get("model", "")
        self.api_base = config.get("api_base", "")
        self.proxy_config = proxy_config or {}
        
    def get_proxies(self) -> Dict[str, str]:
        """获取代理设置
        
        Returns:
            代理设置字典
        """
        if not self.proxy_config.get("enabled", False):
            return {}
            
        proxies = {}
        if http_proxy := self.proxy_config.get("http"):
            proxies["http"] = http_proxy
        if https_proxy := self.proxy_config.get("https"):
            proxies["https"] = https_proxy
            
        return proxies
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], stream: bool = True) -> Union[str, Generator[str, None, None]]:
        """生成回复
        
        Args:
            messages: 消息历史列表，每个消息是一个字典，包含role和content字段
            stream: 是否使用流式输出
            
        Returns:
            如果stream为True，返回一个生成器，每次生成一个字符串片段
            如果stream为False，返回完整的回复字符串
        """
        pass


class OpenAIModel(BaseModel):
    """OpenAI模型接口"""
    
    def __init__(self, config: Dict[str, Any], proxy_config: Dict[str, Any] = None):
        """初始化模型
        
        Args:
            config: 模型配置字典
            proxy_config: 代理配置字典
        """
        super().__init__(config, proxy_config)
    
    def generate(self, messages: List[Dict[str, str]], stream: bool = True) -> Union[str, Generator[str, None, None]]:
        """生成回复
        
        Args:
            messages: 消息历史列表
            stream: 是否使用流式输出
            
        Returns:
            回复内容
        """
        try:
            # 使用requests库直接调用OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model_name,
                "messages": messages,
                "stream": stream
            }
            
            if stream:
                return self._stream_generate(headers, data)
            else:
                return self._non_stream_generate(headers, data)
        except Exception as e:
            error_msg = f"OpenAI API请求失败：{str(e)}"
            print(error_msg)
            if stream:
                def error_generator():
                    yield error_msg
                return error_generator()
            else:
                return error_msg
    
    def _stream_generate(self, headers: Dict[str, str], data: Dict[str, Any]) -> Generator[str, None, None]:
        """流式生成回复
        
        Args:
            headers: 请求头
            data: 请求数据
            
        Returns:
            生成器，每次生成一个字符串片段
        """
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            proxies=self.get_proxies()
        )
        
        if response.status_code != 200:
            error_msg = f"API请求失败：{response.status_code} {response.text}"
            print(error_msg)
            yield error_msg
            return
        
        for line in response.iter_lines():
            if not line:
                continue
                
            # 跳过 data: 前缀
            line = line.decode('utf-8')
            if line.startswith('data: '):
                line = line[6:]
                
            # 跳过心跳消息
            if line == '[DONE]':
                break
                
            try:
                data = json.loads(line)
                if 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    content = delta.get('content')
                    if content:
                        yield content
            except Exception as e:
                print(f"解析响应时出错：{e}")
    
    def _non_stream_generate(self, headers: Dict[str, str], data: Dict[str, Any]) -> str:
        """非流式生成回复
        
        Args:
            headers: 请求头
            data: 请求数据
            
        Returns:
            完整的回复字符串
        """
        # 非流式请求
        data['stream'] = False
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data,
            proxies=self.get_proxies()
        )
        
        if response.status_code != 200:
            return f"API请求失败：{response.status_code} {response.text}"
        
        try:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            return ""
        except Exception as e:
            return f"解析响应时出错：{e}"


class DeepSeekModel(OpenAIModel):
    """DeepSeek模型接口
    
    由于DeepSeek API兼容OpenAI接口，因此直接继承OpenAIModel类
    """
    
    pass


class QwenModel(BaseModel):
    """阿里云通义千问模型接口"""
    
    def generate(self, messages: List[Dict[str, str]], stream: bool = True) -> Union[str, Generator[str, None, None]]:
        """生成回复
        
        Args:
            messages: 消息历史列表
            stream: 是否使用流式输出
            
        Returns:
            回复内容
        """
        try:
            # 通义千问API与OpenAI API不完全兼容，使用requests库直接调用
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model_name,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "stream": stream
                }
            }
            
            if stream:
                return self._stream_generate(headers, data)
            else:
                return self._non_stream_generate(headers, data)
        except Exception as e:
            error_msg = f"通义千问API请求失败：{str(e)}"
            print(error_msg)
            if stream:
                def error_generator():
                    yield error_msg
                return error_generator()
            else:
                return error_msg
    
    def _stream_generate(self, headers: Dict[str, str], data: Dict[str, Any]) -> Generator[str, None, None]:
        """流式生成回复
        
        Args:
            headers: 请求头
            data: 请求数据
            
        Returns:
            生成器，每次生成一个字符串片段
        """
        response = requests.post(
            f"{self.api_base}/services/aigc/text-generation/generation",
            headers=headers,
            json=data,
            stream=True,
            proxies=self.get_proxies()
        )
        
        if response.status_code != 200:
            error_msg = f"API请求失败：{response.status_code} {response.text}"
            print(error_msg)
            yield error_msg
            return
        
        for line in response.iter_lines():
            if not line:
                continue
                
            try:
                data = json.loads(line.decode("utf-8"))
                output = data.get("output", {})
                text = output.get("text", "")
                if text:
                    yield text
            except Exception as e:
                print(f"解析响应时出错：{e}")
    
    def _non_stream_generate(self, headers: Dict[str, str], data: Dict[str, Any]) -> str:
        """非流式生成回复
        
        Args:
            headers: 请求头
            data: 请求数据
            
        Returns:
            完整的回复字符串
        """
        response = requests.post(
            f"{self.api_base}/services/aigc/text-generation/generation",
            headers=headers,
            json=data,
            proxies=self.get_proxies()
        )
        
        if response.status_code != 200:
            return f"API请求失败：{response.status_code} {response.text}"
        
        try:
            data = response.json()
            return data.get("output", {}).get("text", "")
        except Exception as e:
            return f"解析响应时出错：{e}"


def get_model_instance(model_name: str, config: Config) -> Optional[BaseModel]:
    """获取模型实例
    
    Args:
        model_name: 模型名称
        config: 配置对象
        
    Returns:
        模型实例，如果模型不存在则返回None
    """
    model_config = config.get_model_config(model_name)
    if not model_config:
        return None
    
    # 检查API密钥是否设置
    if not model_config.get("api_key"):
        # 尝试从环境变量获取API密钥
        env_var_name = f"{model_name.upper()}_API_KEY"
        api_key = os.environ.get(env_var_name)
        if api_key:
            model_config["api_key"] = api_key
        else:
            print(f"警告：未设置{model_name}的API密钥，请在配置文件中设置或通过环境变量{env_var_name}提供")
            return None
    
    # 获取代理配置
    proxy_config = config.proxy
    
    # 根据模型名称创建相应的模型实例
    if model_name.lower() == "openai":
        return OpenAIModel(model_config, proxy_config)
    elif model_name.lower() == "deepseek":
        return DeepSeekModel(model_config, proxy_config)
    elif model_name.lower() == "qwen":
        return QwenModel(model_config, proxy_config)
    else:
        print(f"错误：不支持的模型类型 '{model_name}'")
        return None