#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shell-ai-ask",
    version="0.1.3",
    author="hyizhou",
    author_email="hyizhou@outlook.com",
    description="轻量级命令行AI助手工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyizhou/shell-ai-ask",
    packages=find_packages(),
    py_modules=["main", "config", "models", "conversation"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        ":sys_platform == 'win32'": ["pyreadline3>=3.4.1"],
    },
    entry_points={
        "console_scripts": [
            "ask=main:main",
        ],
    },
)