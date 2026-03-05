/**
 * 历史记录 API Hooks
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { HistoryItem } from './types';

// 获取案例历史记录
export const useCaseHistoryQuery = (caseId: string) => {
  return useQuery<HistoryItem[]>({
    queryKey: ['history', caseId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/history`);
      return response.data;
    },
    enabled: !!caseId,
  });
};
