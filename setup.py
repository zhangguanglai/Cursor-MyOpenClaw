"""Setup script for OpenClaw Core"""

from setuptools import setup, find_packages

setup(
    name="openclaw-core",
    version="0.1.0",
    description="基于 OpenClaw 的 AI 原生研发内核",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "pyyaml>=6.0.0",
    ],
    python_requires=">=3.11",
)
