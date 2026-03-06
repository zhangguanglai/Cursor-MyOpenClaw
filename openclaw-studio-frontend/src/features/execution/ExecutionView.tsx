import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  List,
  Typography,
  Button,
  Spin,
  Modal,
  Space,
  Input,
  Select,
  Tag,
  Tooltip,
  message,
  Popconfirm,
  Breadcrumb,
  Alert,
} from 'antd'
import { CopyOutlined, CheckCircleOutlined, PlayCircleOutlined, EyeOutlined, HomeOutlined } from '@ant-design/icons'
import { useState } from 'react'
import { useCasePatchesQuery, useCaseTasksQuery, useGenerateCodeMutation, useApplyPatchMutation } from '../../services/coding'
import { useCaseQuery } from '../../services/cases'
import type { PatchOut } from '../../services/types'
import DiffPreview from '../../components/DiffPreview'
import { useQueryClient } from '@tanstack/react-query'
import GitStatus from '../../components/GitStatus'

const { Text, Paragraph, Title } = Typography
const { Option } = Select

const ExecutionView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  // 所有 hooks 必须在条件返回之前调用
  const { data: caseData, isLoading: isCaseLoading, error: caseError } = useCaseQuery(caseId || '')
  
  // 获取任务列表（用于生成补丁）
  const { data: tasks = [], isLoading: isTasksLoading } = useCaseTasksQuery(caseId || '')
  
  // 获取补丁列表
  const { data: patches = [], isLoading: isPatchesLoading } = useCasePatchesQuery(caseId || '')
  
  // 生成补丁 Mutation
  const [selectedTaskId, setSelectedTaskId] = useState<string>('')
  const generateMutation = useGenerateCodeMutation(caseId || '', selectedTaskId)
  
  // 应用补丁 Mutation
  const applyMutation = useApplyPatchMutation()
  
  // 状态管理
  const [filterTaskId, setFilterTaskId] = useState<string>('')
  const [filterPath, setFilterPath] = useState<string>('')
  const [sortBy, setSortBy] = useState<'task_id' | 'created_at'>('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [selectedPatch, setSelectedPatch] = useState<PatchOut | null>(null)
  const [showDiffModal, setShowDiffModal] = useState(false)

  // 错误处理（在所有 hooks 之后）
  if (caseError) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="加载案例失败"
          description={caseError instanceof Error ? caseError.message : '未知错误'}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/cases')}>
              返回需求中心
            </Button>
          }
        />
      </div>
    )
  }

  if (!caseId) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="案例 ID 不存在"
          description="请从需求中心选择一个案例"
          type="warning"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/cases')}>
              返回需求中心
            </Button>
          }
        />
      </div>
    )
  }

  if (isCaseLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <Spin size="large" />
        <p style={{ marginTop: 16 }}>加载案例信息...</p>
      </div>
    )
  }

  // 本地过滤 & 排序
  const filteredSortedPatches = [...patches]
    .filter((p) => !filterTaskId || p.task_id === filterTaskId)
    .filter((p) => !filterPath || p.file_path.includes(filterPath))
    .sort((a, b) => {
      const aVal = a[sortBy]
      const bVal = b[sortBy]
      if (aVal === undefined || bVal === undefined) return 0
      if (sortBy === 'created_at') {
        return sortOrder === 'asc'
          ? new Date(aVal).getTime() - new Date(bVal).getTime()
          : new Date(bVal).getTime() - new Date(aVal).getTime()
      }
      return sortOrder === 'asc' ? String(aVal).localeCompare(String(bVal)) : String(bVal).localeCompare(String(aVal))
    })

  // 复制工具函数
  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success(`✅ 已复制${type}`)
    })
  }

  // 触发生成
  const handleGenerate = () => {
    if (!selectedTaskId) return
    const task = tasks.find((t: any) => t.id === selectedTaskId)
    if (!task) return

    generateMutation.mutate(
      {
        task_title: task.title,
        task_description: task.description || '',
        related_files: task.related_files || [],
      },
      {
        onSuccess: () => {
          message.success('✅ 补丁生成成功')
          setSelectedTaskId('')
        },
        onError: (error: any) => {
          message.error(`❌ 生成失败：${error?.message || '未知错误'}`)
        },
      }
    )
  }

  // 触发应用
  const handleApply = (patch: PatchOut) => {
    if (!patch.id) {
      message.warning('补丁 ID 不存在')
      return
    }
    applyMutation.mutate(
      { caseId: caseId || '', patchId: patch.id },
      {
        onSuccess: () => {
          message.success('✅ 补丁已标记为已应用')
          // 本地更新状态（乐观更新）
          queryClient.setQueryData<PatchOut[]>(['patches', caseId], (old) =>
            old?.map((p) => (p.id === patch.id ? { ...p, applied_at: new Date().toISOString(), status: 'applied' } : p)) || []
          )
        },
        onError: () => {
          message.error('❌ 应用失败')
        },
      }
    )
  }

  // 渲染状态 Tag
  const renderStatusTag = (patch: PatchOut) => {
    if (patch.applied_at || patch.status === 'applied') {
      return <Tag color="success">已应用</Tag>
    }
    return <Tag color="processing">已生成</Tag>
  }

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          {
            href: '/cases',
            title: (
              <>
                <HomeOutlined />
                <span>需求中心</span>
              </>
            ),
          },
          {
            title: caseData?.title || `案例 ${caseId}`,
          },
          {
            title: '执行视图',
          },
        ]}
      />
      {caseData ? (
        <>
          <Card style={{ marginBottom: 16 }}>
            <Title level={4}>{caseData.title}</Title>
            <p style={{ color: '#666', marginBottom: 0 }}>{caseData.description}</p>
          </Card>
          {caseId && (
            <div style={{ marginBottom: 16 }}>
              <GitStatus caseId={caseId} />
            </div>
          )}
        </>
      ) : (
        <Alert
          message="案例不存在"
          description={`案例 ${caseId} 不存在或已被删除`}
          type="warning"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/cases')}>
              返回需求中心
            </Button>
          }
        />
      )}
      {/* 生成补丁区域 */}
      <Card title="生成补丁" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>选择任务：</Text>
            <Select
              placeholder="请选择任务"
              style={{ width: 300, marginRight: 8 }}
              loading={isTasksLoading}
              value={selectedTaskId}
              onChange={setSelectedTaskId}
              allowClear
            >
              {tasks.map((task: any) => (
                <Option key={task.id} value={task.id}>
                  {task.title} ({task.id})
                </Option>
              ))}
            </Select>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleGenerate}
              loading={generateMutation.isPending}
              disabled={!selectedTaskId || generateMutation.isPending}
            >
              生成补丁
            </Button>
          </div>
          {generateMutation.isError && (
            <Text type="danger">❌ 生成失败：{(generateMutation.error as any)?.message || '未知错误'}</Text>
          )}
        </Space>
      </Card>

      {/* 补丁列表控制栏 */}
      <Card title="补丁列表" style={{ marginBottom: 24 }}>
        <Space wrap>
          <Input.Search
            placeholder="按文件路径筛选"
            allowClear
            onSearch={setFilterPath}
            style={{ width: 200 }}
          />
          <Select
            placeholder="按任务筛选"
            style={{ width: 200 }}
            value={filterTaskId}
            onChange={setFilterTaskId}
            allowClear
          >
            {tasks.map((task: any) => (
              <Option key={task.id} value={task.id}>
                {task.title} ({task.id})
              </Option>
            ))}
          </Select>
          <Select
            placeholder="排序字段"
            value={sortBy}
            onChange={setSortBy}
            style={{ width: 120 }}
          >
            <Option value="task_id">任务 ID</Option>
            <Option value="created_at">生成时间</Option>
          </Select>
          <Select
            placeholder="排序顺序"
            value={sortOrder}
            onChange={setSortOrder}
            style={{ width: 120 }}
          >
            <Option value="asc">升序</Option>
            <Option value="desc">降序</Option>
          </Select>
        </Space>
      </Card>

      {/* 补丁列表 */}
      <Card title="补丁详情" style={{ marginBottom: 24 }}>
        {isPatchesLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" tip="加载补丁列表..." />
          </div>
        ) : filteredSortedPatches.length === 0 ? (
          <Alert
            message="暂无补丁"
            description={
              tasks.length === 0
                ? '请先在规划视图中生成计划并创建任务，然后返回此处生成补丁。'
                : '请选择一个任务并点击「生成补丁」按钮来生成代码补丁。'
            }
            type="info"
            showIcon
          />
        ) : (
          <List
            dataSource={filteredSortedPatches}
            renderItem={(patch) => (
              <List.Item key={patch.id || patch.task_id}>
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>{patch.file_path}</Text>
                      {renderStatusTag(patch)}
                    </Space>
                  }
                  description={
                    <>
                      <Text type="secondary">任务：{patch.task_id}</Text> •{' '}
                      <Text type="secondary">描述：{patch.description}</Text>
                      {patch.created_at && (
                        <>
                          {' • '}
                          <Text type="secondary">生成时间：{new Date(patch.created_at).toLocaleString()}</Text>
                        </>
                      )}
                      {patch.applied_at && (
                        <>
                          {' • '}
                          <Text type="success">应用时间：{new Date(patch.applied_at).toLocaleString()}</Text>
                        </>
                      )}
                    </>
                  }
                />
                <Space>
                  <Tooltip title="查看 Diff">
                    <Button
                      size="small"
                      icon={<EyeOutlined />}
                      onClick={() => {
                        setSelectedPatch(patch)
                        setShowDiffModal(true)
                      }}
                    >
                      查看
                    </Button>
                  </Tooltip>
                  <Tooltip title="复制补丁内容">
                    <Button
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => copyToClipboard(patch.content, '补丁内容')}
                    />
                  </Tooltip>
                  <Tooltip title="复制文件路径">
                    <Button
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => copyToClipboard(patch.file_path, '文件路径')}
                    />
                  </Tooltip>
                  <Tooltip title="复制描述">
                    <Button
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => copyToClipboard(patch.description, '描述')}
                    />
                  </Tooltip>
                  <Popconfirm
                    title="确认应用此补丁？"
                    onConfirm={() => handleApply(patch)}
                    okButtonProps={{ loading: applyMutation.isPending && applyMutation.variables?.patchId === patch.id }}
                  >
                    <Button
                      size="small"
                      type="primary"
                      icon={<CheckCircleOutlined />}
                      disabled={!!patch.applied_at || patch.status === 'applied'}
                    >
                      应用
                    </Button>
                  </Popconfirm>
                </Space>
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* Diff 预览 Modal */}
      <Modal
        title="Diff 预览"
        open={showDiffModal}
        onCancel={() => setShowDiffModal(false)}
        footer={null}
        width="90%"
        style={{ top: 20 }}
      >
        {selectedPatch && (
          <DiffPreview patchContent={selectedPatch.content} fileName={selectedPatch.file_path} />
        )}
      </Modal>
    </div>
  )
}

export default ExecutionView
