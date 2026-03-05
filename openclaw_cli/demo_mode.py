"""
演示模式 - 使用模拟数据展示完整闭环

当没有配置 API Key 时，可以使用此模式演示完整流程。
"""

import json
from pathlib import Path
from openclaw_studio.case_manager import CaseManager


def run_demo_loop():
    """运行演示闭环"""
    print("=" * 60)
    print("OpenClaw 完整闭环演示")
    print("=" * 60)
    print()

    manager = CaseManager()

    # 1. 创建案例（如果还没有）
    case_id = "case-eca55ddc"
    case = manager.get_case(case_id)
    if not case:
        print("[1/7] 创建案例...")
        case = manager.create_case(
            title="添加日志记录功能",
            description="为 OpenClaw Core 添加日志记录功能，支持多级别、文件输出和日志轮转",
            repo_path=".",
            branch="main",
        )
        print(f"     案例已创建: {case.id}")
    else:
        print(f"[1/7] 使用现有案例: {case.id}")

    print()

    # 2. 生成计划（使用模拟数据）
    print("[2/7] 生成实现计划...")
    plan_md = """# 实现计划：添加日志记录功能

## 概述
为 OpenClaw Core 添加统一的日志记录功能，使用 Python 标准库 logging 模块。

## 涉及模块
- `openclaw_core/logger.py` (新建)
- `openclaw_core/__init__.py` (修改)
- `config/logger.yml` (新建，可选)

## 任务拆解

### 任务 1: 创建日志模块基础结构
- 创建 `openclaw_core/logger.py`
- 定义 Logger 类
- 实现基础日志方法（debug, info, warning, error）

### 任务 2: 实现日志配置
- 支持从配置文件加载
- 支持控制台和文件输出
- 支持日志级别配置

### 任务 3: 实现日志轮转
- 使用 RotatingFileHandler 实现按大小轮转
- 使用 TimedRotatingFileHandler 实现按时间轮转

### 任务 4: 集成到现有模块
- 在 LLMRouter 中添加日志
- 在 Agent 中添加日志
- 更新 __init__.py 导出 Logger

## 风险分析
- 低风险：使用标准库，不引入新依赖
- 性能影响：最小，日志是异步写入

## 测试建议
- 单元测试：测试各个日志级别
- 集成测试：测试日志文件生成和轮转
"""

    tasks = [
        {
            "id": "task-001",
            "title": "创建日志模块基础结构",
            "description": "创建 openclaw_core/logger.py，定义基础 Logger 类",
            "estimated_steps": [
                "创建 logger.py 文件",
                "定义 Logger 类",
                "实现基础日志方法（debug, info, warning, error）",
            ],
            "related_files": ["openclaw_core/logger.py"],
            "risk_level": "low",
        },
        {
            "id": "task-002",
            "title": "实现日志配置",
            "description": "支持从配置文件加载，支持控制台和文件输出",
            "estimated_steps": [
                "实现配置加载逻辑",
                "添加控制台 Handler",
                "添加文件 Handler",
            ],
            "related_files": ["openclaw_core/logger.py", "config/logger.yml"],
            "risk_level": "low",
        },
        {
            "id": "task-003",
            "title": "实现日志轮转",
            "description": "使用 RotatingFileHandler 和 TimedRotatingFileHandler",
            "estimated_steps": [
                "实现按大小轮转",
                "实现按时间轮转",
                "添加配置选项",
            ],
            "related_files": ["openclaw_core/logger.py"],
            "risk_level": "medium",
        },
        {
            "id": "task-004",
            "title": "集成到现有模块",
            "description": "在 LLMRouter 和 Agent 中添加日志",
            "estimated_steps": [
                "在 LLMRouter 中添加日志调用",
                "在 Agent 中添加日志调用",
                "更新 __init__.py",
            ],
            "related_files": ["openclaw_core/llm_router.py", "openclaw_core/agents.py", "openclaw_core/__init__.py"],
            "risk_level": "low",
        },
    ]

    plan = manager.save_plan(case_id, plan_md, tasks)
    print(f"     计划已生成: {plan.id}")
    print(f"     任务数量: {len(tasks)}")
    print()

    # 3. 查看计划
    print("[3/7] 查看实现计划...")
    plan_data = manager.get_plan(case_id)
    print(f"     计划文件: {plan_data['plan'].plan_md_path}")
    print(f"     任务列表: {len(plan_data['tasks'])} 个任务")
    for i, task in enumerate(plan_data['tasks'], 1):
        print(f"       {i}. {task['title']} (风险: {task.get('risk_level', 'N/A')})")
    print()

    # 4. 为第一个任务生成代码（模拟）
    print("[4/7] 为任务生成代码补丁...")
    task_id = "task-001"
    patch_content = """--- /dev/null
+++ b/openclaw_core/logger.py
@@ -0,0 +1,45 @@
+import logging
+import logging.handlers
+from pathlib import Path
+from typing import Optional
+
+
+class Logger:
+    \"\"\"OpenClaw 日志记录器\"\"\"
+    
+    def __init__(self, name: str = "openclaw", level: str = "INFO"):
+        \"\"\"
+        初始化日志记录器
+        
+        Args:
+            name: 日志记录器名称
+            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
+        \"\"\"
+        self.logger = logging.getLogger(name)
+        self.logger.setLevel(getattr(logging, level.upper()))
+        
+        # 避免重复添加 Handler
+        if not self.logger.handlers:
+            # 控制台 Handler
+            console_handler = logging.StreamHandler()
+            console_handler.setFormatter(
+                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
+            )
+            self.logger.addHandler(console_handler)
+    
+    def debug(self, message: str):
+        \"\"\"记录 DEBUG 级别日志\"\"\"
+        self.logger.debug(message)
+    
+    def info(self, message: str):
+        \"\"\"记录 INFO 级别日志\"\"\"
+        self.logger.info(message)
+    
+    def warning(self, message: str):
+        \"\"\"记录 WARNING 级别日志\"\"\"
+        self.logger.warning(message)
+    
+    def error(self, message: str):
+        \"\"\"记录 ERROR 级别日志\"\"\"
+        self.logger.error(message)
+    
+    def add_file_handler(self, file_path: Path, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
+        \"\"\"
+        添加文件 Handler（支持日志轮转）
+        
+        Args:
+            file_path: 日志文件路径
+            max_bytes: 单个日志文件最大大小（字节）
+            backup_count: 保留的备份文件数量
+        \"\"\"
+        file_handler = logging.handlers.RotatingFileHandler(
+            file_path,
+            maxBytes=max_bytes,
+            backupCount=backup_count,
+            encoding='utf-8'
+        )
+        file_handler.setFormatter(
+            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
+        )
+        self.logger.addHandler(file_handler)
+"""
    
    patch_path = manager.save_patch(case_id, task_id, patch_content, "创建日志模块基础结构")
    manager.update_task_status(task_id, "completed")
    print(f"     补丁已生成: {patch_path}")
    print(f"     任务状态: completed")
    print()

    # 5. 为第二个任务生成代码
    print("[5/7] 为第二个任务生成代码...")
    task_id_2 = "task-002"
    patch_content_2 = """--- a/openclaw_core/logger.py
+++ b/openclaw_core/logger.py
@@ -1,6 +1,7 @@
 import logging
 import logging.handlers
 from pathlib import Path
+import yaml
 from typing import Optional
 
 
@@ -45,6 +46,30 @@ class Logger:
         )
         self.logger.addHandler(file_handler)
+    
+    @classmethod
+    def from_config(cls, config_path: Optional[Path] = None):
+        \"\"\"
+        从配置文件创建 Logger
+        
+        Args:
+            config_path: 配置文件路径，默认查找 config/logger.yml
+        \"\"\"
+        if config_path is None:
+            config_path = Path(__file__).parent.parent / "config" / "logger.yml"
+        
+        if config_path.exists():
+            with open(config_path, 'r', encoding='utf-8') as f:
+                config = yaml.safe_load(f)
+        else:
+            config = {}
+        
+        name = config.get('name', 'openclaw')
+        level = config.get('level', 'INFO')
+        logger = cls(name=name, level=level)
+        
+        # 如果配置了文件输出
+        if 'file' in config:
+            file_path = Path(config['file']['path'])
+            max_bytes = config['file'].get('max_bytes', 10 * 1024 * 1024)
+            backup_count = config['file'].get('backup_count', 5)
+            logger.add_file_handler(file_path, max_bytes, backup_count)
+        
+        return logger
"""
    
    manager.save_patch(case_id, task_id_2, patch_content_2, "实现日志配置")
    manager.update_task_status(task_id_2, "completed")
    print(f"     补丁已生成: {task_id_2}.patch")
    print()

    # 6. 生成测试建议
    print("[6/7] 生成测试建议...")
    suggestions = """# 测试建议

## 潜在问题

- [medium] 当配置文件不存在时，应该使用默认配置而不是抛出异常
- [low] 日志文件路径不存在时，应该自动创建目录

## 测试用例

### test_logger_basic
- 创建 Logger 实例
- 调用各个日志级别方法
- 验证日志输出

### test_logger_file_handler
- 创建带文件 Handler 的 Logger
- 写入日志
- 验证日志文件生成

### test_logger_rotation
- 创建带轮转的 Logger
- 写入大量日志触发轮转
- 验证备份文件生成

### test_logger_from_config
- 创建配置文件
- 使用 from_config 创建 Logger
- 验证配置生效
"""
    
    checklist = [
        "运行单元测试验证所有日志级别正常工作",
        "检查日志文件是否正确生成",
        "验证日志轮转功能（写入大量日志）",
        "测试配置文件加载功能",
        "验证日志格式是否符合要求",
    ]
    
    manager.save_test_results(case_id, suggestions, checklist)
    manager.update_case_status(case_id, "testing")
    print(f"     测试建议已生成")
    print(f"     潜在问题: 2 个")
    print(f"     测试用例: 4 个")
    print(f"     验收清单: {len(checklist)} 项")
    print()

    # 7. 生成总结
    print("[7/7] 生成案例总结...")
    summary = """# 案例总结：添加日志记录功能

## 完成情况

✅ 已完成所有任务：
1. 创建日志模块基础结构
2. 实现日志配置
3. 实现日志轮转（部分）
4. 集成到现有模块（待完成）

## 生成的文件

- `openclaw_core/logger.py` - 日志模块
- `config/logger.yml` - 日志配置（待创建）
- 补丁文件：2 个

## 下一步

1. 应用代码补丁
2. 创建配置文件
3. 运行测试
4. 集成到现有模块
5. 更新文档

## 经验总结

- 使用标准库 logging 模块，无需引入新依赖
- 日志轮转功能需要进一步测试
- 配置文件格式需要标准化
"""
    
    manager.save_summary(case_id, summary)
    manager.update_case_status(case_id, "completed")
    print(f"     总结已生成")
    print()

    # 显示结果
    print("=" * 60)
    print("完整闭环演示完成！")
    print("=" * 60)
    print()
    print("生成的文件：")
    case_dir = Path("cases") / case_id
    if case_dir.exists():
        for file in case_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(case_dir)
                print(f"  - {rel_path}")
    print()
    print(f"查看详细内容：")
    print(f"  计划: cases/{case_id}/plan.md")
    print(f"  补丁: cases/{case_id}/patches/")
    print(f"  测试: cases/{case_id}/tests/")
    print(f"  总结: cases/{case_id}/summary.md")


if __name__ == '__main__':
    run_demo_loop()
