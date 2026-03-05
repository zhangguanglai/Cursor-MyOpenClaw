/**
 * 历史记录 API Hooks
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from './apiClient';
import type { HistoryItem, CaseHistoryOut } from './types';

export interface HistoryQueryParams {
  types?: string[]
  startTime?: string
  endTime?: string
  search?: string
}

// 获取案例历史记录
export const useCaseHistoryQuery = (caseId: string, params?: HistoryQueryParams) => {
  return useQuery<CaseHistoryOut>({
    queryKey: ['history', caseId, params],
    queryFn: async () => {
      const url = new URL(`/api/v1/cases/${caseId}/history`, apiClient.defaults.baseURL)
      if (params) {
        Object.entries(params).forEach(([k, v]) => {
          if (v !== undefined && v !== null && v !== '') {
            url.searchParams.append(k, Array.isArray(v) ? v.join(',') : String(v))
          }
        })
      }
      const response = await apiClient.get(url.pathname + url.search)
      return response.data
    },
    enabled: !!caseId,
  })
}
