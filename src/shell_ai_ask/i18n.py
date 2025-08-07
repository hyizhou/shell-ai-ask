#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
国际化模块
提供多语言支持功能
"""

import os
import json
import locale
from typing import Dict, Any, Optional


class I18n:
    """国际化管理类"""
    
    def __init__(self, language: Optional[str] = None):
        """初始化国际化模块
        
        Args:
            language: 语言代码，如果为None则自动检测系统语言
        """
        self.language = language or self._detect_system_language()
        self.translations = self._load_translations()
    
    def _detect_system_language(self) -> str:
        """检测系统语言
        
        Returns:
            语言代码（如 'zh', 'en'）
        """
        try:
            # 获取系统默认语言
            system_lang = locale.getdefaultlocale()[0]
            if system_lang:
                # 提取语言代码（如 zh_CN -> zh）
                lang_code = system_lang.lower().split('_')[0]
                # 检查是否支持该语言，只支持中文和英文
                if lang_code in ['zh', 'en']:
                    return lang_code
                # 如果是中文相关变体，统一使用zh
                elif lang_code.startswith('zh'):
                    return 'zh'
        except:
            pass
        
        # 默认使用英语
        return 'en'
    
    def _load_translations(self) -> Dict[str, Any]:
        """加载翻译文件
        
        Returns:
            翻译字典
        """
        # 获取翻译文件路径
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        translation_file = os.path.join(translations_dir, f'{self.language}.json')
        
        # 如果特定语言的翻译文件不存在，使用英语作为后备
        if not os.path.exists(translation_file):
            translation_file = os.path.join(translations_dir, 'en.json')
        
        # 如果后备文件也不存在，返回空字典
        if not os.path.exists(translation_file):
            return {}
        
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告：无法加载翻译文件 {translation_file}: {e}")
            return {}
    
    def t(self, key: str, **kwargs) -> str:
        """获取翻译文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        # 获取翻译文本
        text = self.translations.get(key, key)
        
        # 格式化文本
        try:
            return text.format(**kwargs)
        except KeyError:
            # 如果格式化失败，返回原始文本
            return text
    
    def get_available_languages(self) -> list:
        """获取可用的语言列表
        
        Returns:
            语言代码列表，只包含中文和英文
        """
        return ['zh', 'en']
    
    def set_language(self, language: str) -> bool:
        """设置语言
        
        Args:
            language: 语言代码
            
        Returns:
            是否设置成功
        """
        if language in self.get_available_languages():
            self.language = language
            self.translations = self._load_translations()
            return True
        return False


# 全局国际化实例
_i18n_instance = None


def get_i18n() -> I18n:
    """获取全局国际化实例
    
    Returns:
        国际化实例
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """快捷翻译函数
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    return get_i18n().t(key, **kwargs)


def init_i18n(language: Optional[str] = None) -> I18n:
    """初始化国际化模块
    
    Args:
        language: 语言代码，如果为None则自动检测
        
    Returns:
        国际化实例
    """
    global _i18n_instance
    _i18n_instance = I18n(language)
    return _i18n_instance