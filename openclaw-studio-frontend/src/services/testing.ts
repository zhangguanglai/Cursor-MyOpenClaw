/**
 * 测试 API Hooks
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { TestRequestIn, TestResponseOut } from './types';

// 生成测试建议
export const useGenerateTestMutation = (caseId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: TestRequestIn) => {
      const response = await apiClient.post(`/api/v1/cases/${caseId}/test`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['testing', caseId] });
    },
  });
};
