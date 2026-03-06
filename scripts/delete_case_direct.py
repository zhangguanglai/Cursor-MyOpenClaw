#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接删除案例脚本（不通过 API）
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.case_manager import CaseManager
import shutil

def delete_case_direct(case_id: str):
    """直接删除案例（不通过 API）"""
    try:
        case_manager = CaseManager()
        
        # 检查案例是否存在
        case = case_manager.get_case(case_id)
        if not case:
            print(f"[失败] 案例 {case_id} 不存在")
            return False
        
        print("=" * 60)
        print(f"准备删除案例: {case_id}")
        print(f"标题: {case.title}")
        print("=" * 60)
        
        # 删除案例
        success = case_manager.delete_case(case_id)
        
        if success:
            print("[成功] 案例删除成功！")
            print(f"已删除案例 ID: {case_id}")
            print("=" * 60)
            return True
        else:
            print("[失败] 删除失败")
            return False
            
    except Exception as e:
        print(f"[错误] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python delete_case_direct.py <case_id>")
        print("示例: python delete_case_direct.py case-2a73c7be")
        sys.exit(1)
    
    case_id = sys.argv[1]
    delete_case_direct(case_id)
