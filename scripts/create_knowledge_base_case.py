"""
创建知识库系统案例
"""

import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.case_manager import CaseManager

def create_knowledge_base_case():
    """创建知识库系统案例"""
    case_manager = CaseManager()
    
    case = case_manager.create_case(
        title="实现知识库系统",
        description="""建立可复制的知识体系，沉淀开发经验和最佳实践。

## 需求描述

实现知识库系统，支持：
1. 建立知识库目录结构（规则、剧本、案例、模板）
2. 实现案例模板系统
3. 实现知识库搜索功能
4. 支持从模板创建新案例
5. 案例总结自动归档

## 技术约束

- 使用文件系统存储知识库内容
- 支持 Markdown 格式
- 提供 RESTful API 接口
- 前端支持搜索和浏览

## 验收标准

- [ ] 创建知识库目录结构
- [ ] 实现案例模板系统
- [ ] 实现知识库搜索 API
- [ ] 支持从模板创建案例
- [ ] 案例总结自动归档
- [ ] 前端知识库浏览界面
- [ ] 前端搜索功能
""",
        repo_path=".",
        branch="main"
    )
    
    print(f"✅ 案例创建成功！")
    print(f"案例 ID: {case.id}")
    print(f"标题: {case.title}")
    print(f"\n下一步：运行以下命令生成计划")
    print(f"python -m openclaw_cli.cli plan {case.id}")

if __name__ == "__main__":
    create_knowledge_base_case()
