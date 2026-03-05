/**
 * 案例管理 API Hooks
 * 
 * 使用 TanStack Query 封装的案例相关 API 调用
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { CaseOut, CaseCreate } from './types';

// 查询所有案例
export const useCasesQuery = () => {
  return useQuery<CaseOut[]>({
    queryKey: ['cases'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/cases');
      return response.data;
    },
  });
};

// 查询单个案例
export const useCaseQuery = (caseId: string) => {
  return useQuery<CaseOut>({
    queryKey: ['cases', caseId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}`);
      return response.data;
    },
    enabled: !!caseId,
  });
};

// 创建案例
export const useCreateCaseMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CaseCreate) => {
      const response = await apiClient.post('/api/v1/cases', data);
      return response.data;
    },
    onSuccess: () => {
      // 使案例列表缓存失效，触发重新获取
      queryClient.invalidateQueries({ queryKey: ['cases'] });
    },
  });
};

// 更新案例
export const useUpdateCaseMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ caseId, data }: { caseId: string; data: Partial<CaseCreate> }) => {
      const response = await apiClient.put(`/api/v1/cases/${caseId}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['cases', variables.caseId] });
    },
  });
};
