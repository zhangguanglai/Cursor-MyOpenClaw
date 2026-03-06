#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
列出所有案例脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.case_manager import CaseManager

def list_cases():
    """列出所有案例"""
    try:
        case_manager = CaseManager()
        cases = case_manager.list_cases()
        
        print("=" * 60)
        print(f"当前案例数量: {len(cases)}")
        print("=" * 60)
        
        if cases:
            for case in cases:
                print(f"ID: {case.id}")
                print(f"标题: {case.title}")
                print(f"状态: {case.status}")
                print(f"创建时间: {case.created_at}")
                print("-" * 60)
        else:
            print("暂无案例")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"[错误] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_cases()
