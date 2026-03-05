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
      let url = `/api/v1/cases/${caseId}/history`
      if (params) {
        const searchParams = new URLSearchParams()
        Object.entries(params).forEach(([k, v]) => {
          if (v !== undefined && v !== null && v !== '') {
            searchParams.append(k, Array.isArray(v) ? v.join(',') : String(v))
          }
        })
        const queryString = searchParams.toString()
        if (queryString) {
          url += `?${queryString}`
        }
      }
      const response = await apiClient.get(url)
      return response.data
    },
    enabled: !!caseId,
  })
}
