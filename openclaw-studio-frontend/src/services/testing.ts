/**
 * 测试 API Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { TestRequestIn, TestResponseOut } from './types';

// 获取测试结果
export const useGetTestResultsQuery = (caseId: string) => {
  return useQuery<TestResponseOut>({
    queryKey: ['testing', caseId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/test`);
      return response.data;
    },
    enabled: !!caseId,
    retry: false, // 如果不存在测试结果，不重试
  });
};

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
