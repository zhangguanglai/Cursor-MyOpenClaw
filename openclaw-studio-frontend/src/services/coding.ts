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
      return response.data;
    },
    enabled: !!caseId,
  });
};
