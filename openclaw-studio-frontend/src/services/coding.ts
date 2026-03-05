/**
 * 编码 API Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { CodingRequestIn, PatchOut } from './types';

// 生成代码补丁
export const useGenerateCodeMutation = (caseId: string, taskId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CodingRequestIn) => {
      const response = await apiClient.post(
        `/api/v1/cases/${caseId}/tasks/${taskId}/code`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patches', caseId] });
    },
  });
};

// 获取补丁列表
export const useCasePatchesQuery = (caseId: string) => {
  return useQuery<PatchOut[]>({
    queryKey: ['patches', caseId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/patches`);
      // 为每个补丁添加 id 和标准化字段
      return response.data.map((patch: any, index: number) => ({
        ...patch,
        id: patch.id || patch.task_id || `patch-${index}`,
        task_id: patch.task_id || patch.id || `task-${index}`,
        content: patch.content || patch.diff || '',
        file_path: patch.file_path || '',
        description: patch.description || '',
        created_at: patch.created_at || new Date().toISOString(),
      } as PatchOut));
    },
    enabled: !!caseId,
  });
};

// 获取任务列表（用于生成补丁）
export const useCaseTasksQuery = (caseId: string) => {
  return useQuery({
    queryKey: ['tasks', caseId],
    queryFn: async () => {
      // 从 plan 接口获取任务列表
      const response = await apiClient.get(`/api/v1/cases/${caseId}/plan`);
      return response.data.tasks || [];
    },
    enabled: !!caseId,
  });
};

// 应用补丁 Mutation
export const useApplyPatchMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ caseId, patchId }: { caseId: string; patchId: string }) => {
      const response = await apiClient.patch(`/api/v1/cases/${caseId}/patches/${patchId}/apply`);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['patches', variables.caseId] });
    },
  });
};
