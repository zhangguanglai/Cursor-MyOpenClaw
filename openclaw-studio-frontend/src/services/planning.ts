/**
 * 规划 API Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { PlanningRequestIn, PlanningResponseOut } from './types';

// 触发规划生成
export const useTriggerPlanningMutation = (caseId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: PlanningRequestIn) => {
      const response = await apiClient.post(`/api/v1/cases/${caseId}/planning`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planning', caseId] });
      queryClient.invalidateQueries({ queryKey: ['cases', caseId] });
    },
  });
};

// 获取计划
export const useCasePlanQuery = (caseId: string) => {
  return useQuery<PlanningResponseOut>({
    queryKey: ['planning', caseId],
    queryFn: async () => {
      try {
        const response = await apiClient.get(`/api/v1/cases/${caseId}/plan`);
        return response.data;
      } catch (error: any) {
        // 如果是 404，说明计划不存在，返回 null 而不是抛出错误
        if (error.response?.status === 404) {
          return null as any;
        }
        throw error;
      }
    },
    enabled: !!caseId,
    retry: false, // 404 不需要重试
  });
};

// 更新计划
export const useUpdatePlanMutation = (caseId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (planMarkdown: string) => {
      const response = await apiClient.put(`/api/v1/cases/${caseId}/plan`, {
        plan_markdown: planMarkdown,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planning', caseId] });
    },
  });
};

// 更新任务状态
export const useUpdateTaskStatusMutation = (caseId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ taskId, status }: { taskId: string; status: 'pending' | 'completed' }) => {
      const response = await apiClient.put(`/api/v1/cases/${caseId}/tasks/${taskId}/status`, {
        status,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planning', caseId] });
    },
  });
};
