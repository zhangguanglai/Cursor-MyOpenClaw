/**
 * 知识库 API 服务
 * 
 * 提供知识库相关的 API 调用接口
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';

// 知识库项类型定义
export interface KnowledgeItem {
  path: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  created_at?: string;
  updated_at?: string;
}

// 搜索响应
export interface SearchResponse {
  results: KnowledgeItem[];
  total: number;
}

/**
 * 搜索知识库
 */
export const useKnowledgeSearchQuery = (
  query: string,
  category?: string,
  tags?: string[]
) => {
  return useQuery<SearchResponse>({
    queryKey: ['knowledge-search', query, category, tags],
    queryFn: async () => {
      const params: Record<string, string> = { q: query };
      if (category) params.category = category;
      if (tags && tags.length > 0) params.tags = tags.join(',');
      
      const response = await apiClient.get('/api/v1/knowledge/search', { params });
      return response.data;
    },
    enabled: !!query && query.length > 0,
  });
};

/**
 * 列出所有模板
 */
export const useTemplatesQuery = () => {
  return useQuery<string[]>({
    queryKey: ['knowledge-templates'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/knowledge/templates');
      return response.data;
    },
  });
};

/**
 * 获取模板内容
 */
export const useTemplateQuery = (templateName: string) => {
  return useQuery<{ template_name: string; content: string }>({
    queryKey: ['knowledge-template', templateName],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/knowledge/templates/${templateName}`);
      return response.data;
    },
    enabled: !!templateName,
  });
};

/**
 * 列出知识库项
 */
export const useKnowledgeItemsQuery = (category?: string) => {
  return useQuery<KnowledgeItem[]>({
    queryKey: ['knowledge-items', category],
    queryFn: async () => {
      const params = category ? { category } : {};
      const response = await apiClient.get('/api/v1/knowledge/items', { params });
      return response.data;
    },
  });
};

/**
 * 归档案例
 */
export const useArchiveCaseMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (caseId: string) => {
      const response = await apiClient.post(`/api/v1/knowledge/cases/${caseId}/archive`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-items'] });
      queryClient.invalidateQueries({ queryKey: ['knowledge-search'] });
    },
  });
};
