### 核心 Agent 定义：PlanningAgent / CodingAgent / TestAgent

> 对应待办 `define-agents`。本文件定义每个 Agent 的：职责边界、输入/输出格式、主要使用的工具列表，以及它们与 LLMRouter 的关系。

---

### 1. 总体设计原则

- **Plan-first**：所有重要改动先规划再编码，PlanningAgent 是入口。
- **小步可控**：CodingAgent 以「补丁建议 + 解释」为主，而不是直接大范围重写。
- **持续评审**：TestAgent 不只关心测试用例，也提供「代码风险与改进建议」。
- **统一依赖 LLMRouter**：三个 Agent 都不直接调用具体 LLM，全部通过 LLMRouter。

---

### 2. PlanningAgent

#### 2.1 职责

- 从自然语言需求 / Issue / PR 描述中：
  - 澄清需求、识别约束与验收标准。
  - 输出结构化的实现计划（Markdown），包含：
    - 涉及模块/文件列表。
    - 新增/修改的接口与数据结构。
    - 任务拆解与优先级。
    - 风险分析与测试建议。
- 生成「可被 CodingAgent 消化的子任务列表」。

#### 2.2 输入格式

```json
{
  "requirement_description": "string, 用户用自然语言写的需求/Issue/PR 描述",
  "codebase_overview": "string, 可选，当前项目结构/关键模块说明",
  "related_files": ["path/to/file1", "path/to/file2"],
  "constraints": [
    "必须兼容现有 API /xxx",
    "性能不显著退化",
    "不改变外部公开接口"
  ],
  "acceptance_criteria": [
    "功能 A 可以通过用例 X/Y 验证",
    "CI 所有现有测试通过"
  ]
}
```

#### 2.3 输出格式

- **Markdown 计划文档**（供人类阅读 + 记录入案例库）。
- **结构化子任务列表**（供内部 Agent 调度使用）：

```json
{
  "plan_markdown": "string, 详细的实现计划",
  "tasks": [
    {
      "id": "task-1",
      "title": "在 XXX 模块中添加 YYYY 功能",
      "description": "更详细的说明...",
      "estimated_steps": [
        "阅读 file_a.py 了解当前逻辑",
        "在 file_b.py 中新增函数 foo",
        "更新接口 /api/v1/xxx 的入参说明"
      ],
      "related_files": ["src/module_a/file_a.py", "src/module_b/file_b.py"],
      "risk_level": "low | medium | high"
    }
  ]
}
```

#### 2.4 需要的工具列表

- **代码读取工具**：按路径读取文件内容。
- **代码搜索工具**：在代码库中查找标识符/路由/接口定义。
- **项目结构工具**：列出目录结构与主要模块说明（可缓存）。

---

### 3. CodingAgent

#### 3.1 职责

- 针对某个具体子任务：
  - 阅读相关代码与上下文。
  - 生成「代码修改建议 + Patch + 解释」。
  - 为关键逻辑给出必要注释与简单测试建议。
- 不直接写入代码，而是输出**可被人类/工具应用的补丁**。

#### 3.2 输入格式

```json
{
  "task": {
    "id": "task-1",
    "title": "string",
    "description": "string",
    "related_files": ["src/module_a/file_a.py"],
    "acceptance_criteria": ["..."]
  },
  "current_files_content": {
    "src/module_a/file_a.py": "文件内容",
    "src/module_b/file_b.py": "文件内容（可选）"
  },
  "coding_guidelines": "string, 可选，项目级代码规范/风格要求",
  "language": "python | typescript | ...",
  "apply_constraints": [
    "只修改列出的文件",
    "避免大范围重构",
    "尽量保持向后兼容"
  ]
}
```

#### 3.3 输出格式

```json
{
  "patches": [
    {
      "file_path": "src/module_a/file_a.py",
      "description": "在函数 foo 中增加参数校验",
      "diff": "统一格式的补丁字符串（如 unified diff 或 Cursor 友好格式）"
    }
  ],
  "rationale": "string, 对关键设计与权衡的解释",
  "followup_suggestions": [
    "建议为函数 foo 添加单元测试用例 test_foo_invalid_input",
    "建议未来重构 XXX 模块，拆分职责"
  ],
  "risks": [
    "如果外部代码依赖 foo 的旧行为，可能需要同步更新调用处"
  ],
  "test_suggestions": [
    "运行现有 test_module_a.py",
    "手工验证接口 /api/v1/xxx 正常返回"
  ]
}
```

#### 3.4 需要的工具列表

- **文件读取/写入工具**：读取/预览文件，最终由人类或自动化应用补丁。
- **代码搜索工具**：查找调用点、类/函数定义。
- **测试运行工具（可选）**：触发特定测试命令并收集结果。

---

### 4. TestAgent

#### 4.1 职责

- 针对一组改动（Patch 或提交）：
  - 识别潜在风险与边界情况。
  - 生成单元测试/集成测试建议。
  - 提供人工验收清单。
- 后续可以扩展为：
  - 直接生成/修改测试代码。
  - 与 CI 集成，根据测试结果给出进一步建议。

#### 4.2 输入格式

```json
{
  "changes": [
    {
      "file_path": "src/module_a/file_a.py",
      "old_content": "string, 可选",
      "new_content": "string",
      "diff": "string, 可选"
    }
  ],
  "context": {
    "related_requirements": ["需求描述或引用 ID"],
    "existing_tests": ["tests/test_module_a.py"],
    "runtime_constraints": ["性能敏感", "对外接口兼容性很重要"]
  }
}
```

#### 4.3 输出格式

```json
{
  "potential_issues": [
    {
      "description": "当输入为 None 时，当前实现可能抛异常",
      "severity": "low | medium | high",
      "related_files": ["src/module_a/file_a.py"]
    }
  ],
  "test_cases": [
    {
      "name": "test_foo_with_invalid_input",
      "type": "unit | integration | e2e",
      "steps": [
        "构造输入 X",
        "调用函数 foo",
        "断言返回值/异常"
      ],
      "target_file": "tests/test_module_a.py"
    }
  ],
  "manual_checklist": [
    "通过接口 /api/v1/xxx 提交合法请求，确认返回正常",
    "在边界条件 Y 下观察日志是否出现异常"
  ]
}
```

#### 4.4 需要的工具列表

- **Diff/版本工具**：获取文件变更内容。
- **测试运行工具**：运行指定测试/测试集。
- **日志/监控查询工具（后续）**：查看运行时错误与性能指标。

---

### 5. Agent 与 LLMRouter 的交互模式

- 三个 Agent 都通过内部的「Agent Runtime」调用 `LLMRouter.complete_chat`：
  - 统一封装系统 Prompt（如项目规则、风格要求）。
  - 统一记录每次调用的请求与响应，用于案例与知识库沉淀。
- 典型调用流程示意：

1. 用户在 OpenClaw Studio 中输入需求。
2. **PlanningAgent**：
   - 调用代码读取/搜索工具收集上下文。
   - 通过 LLMRouter（如模型 `planning` 策略）生成计划与子任务。
3. 你确认/调整计划后，逐个子任务交给 **CodingAgent**：
   - 通过工具获取相关文件内容。
   - 通过 LLMRouter（如模型 `coding` 策略）产出 Patch 建议。
4. 你应用/调整 Patch 后，将改动交给 **TestAgent**：
   - 通过 LLMRouter（如模型 `summary` 策略）生成测试建议与验收清单。

---

### 6. 后续可扩展的 Agent

- **ReviewAgent**（代码评审）：更关注风格、一致性与长期可维护性。
- **RefactorAgent**（重构）：在明确边界的前提下做更大范围的重构。
- **OpsAgent**（运维/平台）：关注部署、监控、容量规划等。

这些可以在当前三大核心 Agent 之上逐步演进，不影响现有设计。

