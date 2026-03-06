#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试案例脚本
"""

import requests
import json
import sys

def create_case():
    """创建测试案例"""
    
    case_data = {
        "title": "实现用户认证系统",
        "description": """为应用添加完整的用户认证功能，包括用户注册、登录、密码重置等功能。

## 需求描述

实现一个完整的用户认证系统，包括以下功能：
- 用户注册：用户可以创建新账户
- 用户登录：用户可以使用邮箱和密码登录
- 密码重置：用户可以重置忘记的密码
- 会话管理：用户登录后保持会话状态
- 安全特性：密码加密存储、防止暴力破解

## 技术要求
- 使用 JWT 进行身份验证
- 密码使用 bcrypt 加密
- 实现登录限流机制
- 支持记住我功能

## 验收标准
- [ ] 用户可以成功注册新账户
- [ ] 用户可以成功登录
- [ ] 用户可以重置密码
- [ ] 会话可以正确保持
- [ ] 密码安全存储
- [ ] 登录限流正常工作"""
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/cases",
            json=case_data,
            timeout=10
        )
        
        if response.status_code == 200:
            case = response.json()
            print("=" * 60)
            print("[成功] 案例创建成功！")
            print("=" * 60)
            print(f"案例 ID: {case['id']}")
            print(f"标题: {case['title']}")
            print(f"状态: {case['status']}")
            print(f"创建时间: {case['created_at']}")
            print("=" * 60)
            print(f"\n前端访问地址: http://localhost:5173/cases/{case['id']}/plan")
            print(f"API 地址: http://localhost:8000/api/v1/cases/{case['id']}")
            print("=" * 60)
            return case
        else:
            print(f"[失败] 创建失败: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"[错误] {e}")
        return None

if __name__ == "__main__":
    create_case()
