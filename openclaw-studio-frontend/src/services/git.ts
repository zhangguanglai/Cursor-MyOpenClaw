/**
 * Git API 服务
 * 
 * 提供 Git 相关的 API 调用接口
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './apiClient';

// Git 状态类型定义
export interface GitStatus {
  case_id: string;
  repo_path: string;
  status: {
    branch: string;
    is_dirty: boolean;
    staged_files: string[];
    unstaged_files: string[];
    untracked_files: string[];
  };
  repo_info: {
    remote_url?: string;
    current_branch: string;
    latest_commit?: {
      hash: string;
      message: string;
      author: string;
      date: string;
    };
    is_dirty: boolean;
  };
}

// Git 分支信息
export interface GitBranches {
  case_id: string;
  current_branch: string;
  branches: string[];
  remote: boolean;
}

// Git Diff
export interface GitDiff {
  case_id: string;
  base: string;
  head: string;
  file_path?: string;
  diff: string;
}

// Git 提交历史
export interface GitCommit {
  hash: string;
  author: string;
  date: string;
  message: string;
}

export interface GitCommits {
  case_id: string;
  branch: string;
  limit: number;
  commits: GitCommit[];
}

/**
 * 获取 Git 状态
 */
export const useGitStatusQuery = (caseId: string) => {
  return useQuery<GitStatus>({
    queryKey: ['git-status', caseId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/git-status`);
      return response.data;
    },
    enabled: !!caseId,
  });
};

/**
 * 获取分支列表
 */
export const useGitBranchesQuery = (caseId: string, remote: boolean = false) => {
  return useQuery<GitBranches>({
    queryKey: ['git-branches', caseId, remote],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/git-branches`, {
        params: { remote },
      });
      return response.data;
    },
    enabled: !!caseId,
  });
};

/**
 * 获取 Git Diff
 */
export const useGitDiffQuery = (
  caseId: string,
  base?: string,
  head?: string,
  filePath?: string
) => {
  return useQuery<GitDiff>({
    queryKey: ['git-diff', caseId, base, head, filePath],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/git-diff`, {
        params: { base, head, file_path: filePath },
      });
      return response.data;
    },
    enabled: !!caseId,
  });
};

/**
 * 获取提交历史
 */
export const useGitCommitsQuery = (caseId: string, limit: number = 10, branch?: string) => {
  return useQuery<GitCommits>({
    queryKey: ['git-commits', caseId, limit, branch],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/git-commits`, {
        params: { limit, branch },
      });
      return response.data;
    },
    enabled: !!caseId,
  });
};

/**
 * 创建新分支
 */
export const useCreateBranchMutation = (caseId: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ branchName, checkout }: { branchName: string; checkout?: boolean }) => {
      const response = await apiClient.post(`/api/v1/cases/${caseId}/git-branches`, null, {
        params: { branch_name: branchName, checkout: checkout ?? true },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['git-branches', caseId] });
      queryClient.invalidateQueries({ queryKey: ['git-status', caseId] });
    },
  });
};
