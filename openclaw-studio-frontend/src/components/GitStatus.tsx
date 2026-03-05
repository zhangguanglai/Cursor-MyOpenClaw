/**
 * Git 状态组件
 * 
 * 显示案例关联的 Git 仓库状态信息
 */

import React from 'react';
import { Card, Tag, Space, Typography, Tooltip, Divider } from 'antd';
import {
  BranchesOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LinkOutlined,
  UserOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useGitStatusQuery } from '../services/git';

const { Text, Paragraph } = Typography;

interface GitStatusProps {
  caseId: string;
}

export const GitStatus: React.FC<GitStatusProps> = ({ caseId }) => {
  const { data, isLoading, error } = useGitStatusQuery(caseId);

  if (isLoading) {
    return <Card loading title="Git 状态" />;
  }

  if (error) {
    return (
      <Card title="Git 状态">
        <Text type="danger">无法获取 Git 状态：{(error as any)?.message || '未知错误'}</Text>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card title="Git 状态">
        <Text type="secondary">该案例未关联 Git 仓库</Text>
      </Card>
    );
  }

  const { status, repo_info } = data;
  const isDirty = status.is_dirty || repo_info.is_dirty;

  return (
    <Card
      title={
        <Space>
          <BranchesOutlined />
          <span>Git 状态</span>
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 当前分支 */}
        <div>
          <Space>
            <Text strong>当前分支：</Text>
            <Tag color="blue" icon={<BranchesOutlined />}>
              {status.branch}
            </Tag>
            {isDirty && (
              <Tag color="orange" icon={<ExclamationCircleOutlined />}>
                有未提交更改
              </Tag>
            )}
            {!isDirty && (
              <Tag color="success" icon={<CheckCircleOutlined />}>
                干净
              </Tag>
            )}
          </Space>
        </div>

        {/* 远程仓库 */}
        {repo_info.remote_url && (
          <div>
            <Space>
              <Text strong>远程仓库：</Text>
              <Tooltip title={repo_info.remote_url}>
                <Text code style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  <LinkOutlined /> {repo_info.remote_url}
                </Text>
              </Tooltip>
            </Space>
          </div>
        )}

        {/* 最新提交 */}
        {repo_info.latest_commit && (
          <>
            <Divider style={{ margin: '8px 0' }} />
            <div>
              <Text strong>最新提交：</Text>
              <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <div>
                    <Text code style={{ fontSize: '12px' }}>
                      {repo_info.latest_commit.hash.substring(0, 8)}
                    </Text>
                    <Text style={{ marginLeft: 8 }}>{repo_info.latest_commit.message}</Text>
                  </div>
                  <Space size="middle">
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      <UserOutlined /> {repo_info.latest_commit.author}
                    </Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      <ClockCircleOutlined /> {new Date(repo_info.latest_commit.date).toLocaleString('zh-CN')}
                    </Text>
                  </Space>
                </Space>
              </Paragraph>
            </div>
          </>
        )}

        {/* 文件状态 */}
        {isDirty && (
          <>
            <Divider style={{ margin: '8px 0' }} />
            <div>
              <Text strong>文件状态：</Text>
              <Space direction="vertical" size="small" style={{ marginTop: 8, width: '100%' }}>
                {status.staged_files.length > 0 && (
                  <div>
                    <Text type="success">已暂存 ({status.staged_files.length})：</Text>
                    <div style={{ marginLeft: 16, marginTop: 4 }}>
                      {status.staged_files.slice(0, 5).map((file, idx) => (
                        <Text key={idx} code style={{ fontSize: '12px', display: 'block' }}>
                          {file}
                        </Text>
                      ))}
                      {status.staged_files.length > 5 && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          ... 还有 {status.staged_files.length - 5} 个文件
                        </Text>
                      )}
                    </div>
                  </div>
                )}
                {status.unstaged_files.length > 0 && (
                  <div>
                    <Text type="warning">未暂存 ({status.unstaged_files.length})：</Text>
                    <div style={{ marginLeft: 16, marginTop: 4 }}>
                      {status.unstaged_files.slice(0, 5).map((file, idx) => (
                        <Text key={idx} code style={{ fontSize: '12px', display: 'block' }}>
                          {file}
                        </Text>
                      ))}
                      {status.unstaged_files.length > 5 && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          ... 还有 {status.unstaged_files.length - 5} 个文件
                        </Text>
                      )}
                    </div>
                  </div>
                )}
                {status.untracked_files.length > 0 && (
                  <div>
                    <Text type="secondary">未跟踪 ({status.untracked_files.length})：</Text>
                    <div style={{ marginLeft: 16, marginTop: 4 }}>
                      {status.untracked_files.slice(0, 5).map((file, idx) => (
                        <Text key={idx} code style={{ fontSize: '12px', display: 'block' }}>
                          {file}
                        </Text>
                      ))}
                      {status.untracked_files.length > 5 && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          ... 还有 {status.untracked_files.length - 5} 个文件
                        </Text>
                      )}
                    </div>
                  </div>
                )}
              </Space>
            </div>
          </>
        )}
      </Space>
    </Card>
  );
};

export default GitStatus;
