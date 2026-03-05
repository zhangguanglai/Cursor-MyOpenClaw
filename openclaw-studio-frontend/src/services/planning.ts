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
      const response = await apiClient.get(`/api/v1/cases/${caseId}/plan`);
      return response.data;
    },
    enabled: !!caseId,
  });
};
