/**
 * TypeScript 类型定义
 * 
 * 与后端 API 模型对应的前端类型定义
 */

export interface CaseCreate {
  title: string;
  description: string;
  repo_path?: string;
  branch?: string;
}

export interface CaseOut {
  id: string;
  title: string;
  description: string;
  repo_path?: string;
  branch?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PlanningRequestIn {
  requirement_description: string;
  related_files?: string[];
}

export interface TaskOut {
  id: string;
  title: string;
  description: string;
  related_files: string[];
  risk_level: string;
  status?: 'pending' | 'completed';
}

export interface PlanningResponseOut {
  plan_id: string;
  plan_markdown: string;
  tasks: TaskOut[];
}

export interface CodingRequestIn {
  task_title: string;
  task_description: string;
  related_files?: string[];
}

export interface PatchOut {
  task_id: string;
  file_path: string;
  description: string;
  content: string;
  id?: string; // 补丁唯一 ID（后端应返回，用于应用/复制）
  created_at?: string; // 生成时间（用于排序）
  applied_at?: string; // 应用时间（null = 未应用）
  status?: 'generated' | 'applied'; // 显式状态（兼容 UI 展示）
}

export interface TestRequestIn {
  patches?: string[];
  related_files?: string[];
}

export interface TestResponseOut {
  test_id?: string;
  potential_issues: Array<{
    description: string;
    severity: string;
    related_files: string[];
  }>;
  test_cases: Array<{
    description: string;
    steps: string[];
    expected_result: string;
  }>;
  checklist?: string[];
  manual_checklist?: string[];
  generated_at?: string;
}

export interface HistoryItem {
  type: string;
  timestamp: string;
  description: string;
  data: any;
}
