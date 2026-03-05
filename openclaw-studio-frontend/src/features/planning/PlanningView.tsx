import { useParams, useNavigate } from 'react-router-dom'
import { Button, Card, Tabs, message, Spin, Alert, Breadcrumb, Typography } from 'antd'
import { SyncOutlined, HomeOutlined } from '@ant-design/icons'
import { useState, useEffect, useMemo } from 'react'
import { useCasePlanQuery, useTriggerPlanningMutation, useUpdatePlanMutation, useUpdateTaskStatusMutation } from '../../services/planning'
import { useCaseQuery } from '../../services/cases'
import type { TaskOut } from '../../services/types'
import { MarkdownEditor } from '../../components/MarkdownEditor'
import { TaskTable, TaskDetailModal } from './TaskTable'
import GitStatus from '../../components/GitStatus'

const { Title } = Typography

const PlanningView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const { data: caseData, isLoading: isCaseLoading, error: caseError } = useCaseQuery(caseId || '')
  const { data: planData, isLoading, error: planError, refetch } = useCasePlanQuery(caseId || '')
  const triggerMutation = useTriggerPlanningMutation(caseId || '')
  const updateMutation = useUpdatePlanMutation(caseId || '')
  const updateTaskStatusMutation = useUpdateTaskStatusMutation(caseId || '')

  // 编辑状态
  const [editingMarkdown, setEditingMarkdown] = useState<string>('')
  const [isEditing, setIsEditing] = useState(false)

  // 任务状态
  const [tasks, setTasks] = useState<TaskOut[]>([])
  const [selectedTask, setSelectedTask] = useState<TaskOut | null>(null)
  const [showDetail, setShowDetail] = useState(false)

  // 初始化数据
  useEffect(() => {
    if (planData) {
      console.log('Plan data loaded:', { 
        hasMarkdown: !!planData.plan_markdown, 
        tasksCount: planData.tasks?.length || 0 
      })
      setEditingMarkdown(planData.plan_markdown || '')
      setTasks(
        (planData.tasks || []).map((t) => ({
          ...t,
          status: (t.status as 'pending' | 'completed') || 'pending',
        }))
      )
    } else {
      // 如果没有计划数据，重置状态
      console.log('No plan data available')
      setEditingMarkdown('')
      setTasks([])
    }
  }, [planData])

  const handleTriggerPlanning = async () => {
    if (!caseData) return
    
    try {
      await triggerMutation.mutateAsync({
        requirement_description: caseData.description,
        related_files: [],
      })
      message.success('规划生成成功')
      refetch()
    } catch (error) {
      console.error('Planning generation error:', error)
      message.error('规划生成失败')
    }
  }

  const handleSavePlan = async (content: string) => {
    try {
      await updateMutation.mutateAsync(content)
      setIsEditing(false)
    } catch (error) {
      console.error('Plan save error:', error)
      message.error('计划保存失败')
    }
  }

  const handleTaskStatusChange = async (taskId: string, status: 'pending' | 'completed') => {
    try {
      await updateTaskStatusMutation.mutateAsync({ taskId, status })
      setTasks(tasks.map(t => t.id === taskId ? { ...t, status } : t))
      message.success('任务状态更新成功')
    } catch (error) {
      console.error('Task status update error:', error)
      message.error('任务状态更新失败')
    }
  }

  const handleTaskClick = (task: TaskOut) => {
    setSelectedTask(task)
    setShowDetail(true)
  }

  // 使用 useMemo 来避免每次渲染都重新创建 tabItems
  const tabItems = useMemo(() => [
    {
      key: 'plan',
      label: '计划',
      children: planData && planData.plan_markdown ? (
        <div style={{ minHeight: '700px' }}>
          <MarkdownEditor
            markdown={editingMarkdown || planData.plan_markdown || ''}
            onSave={handleSavePlan}
            isSaving={updateMutation.isPending}
          />
        </div>
      ) : (
        <Alert message="暂无计划，请点击右上角「生成计划」按钮" type="info" />
      ),
    },
    {
      key: 'tasks',
      label: '任务列表',
      children: tasks.length > 0 ? (
        <TaskTable
          tasks={tasks}
          onStatusChange={handleTaskStatusChange}
          onTaskClick={handleTaskClick}
        />
      ) : (
        <Alert message="暂无任务" type="info" />
      ),
    },
  ], [planData, editingMarkdown, tasks, updateMutation.isPending, handleSavePlan, handleTaskStatusChange, handleTaskClick])

  // 错误处理
  if (caseError) {
    return (
      <div>
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
      <div>
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

  // 如果 caseData 还在加载，显示加载状态
  if (isCaseLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <Spin size="large" />
        <p style={{ marginTop: 16 }}>加载案例信息...</p>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
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
            title: '规划视图',
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
      <Card
        title="实现计划"
        extra={
          <Button
            type="primary"
            icon={<SyncOutlined />}
            onClick={handleTriggerPlanning}
            loading={triggerMutation.isPending}
            disabled={!caseData}
          >
            生成计划
          </Button>
        }
      >
        {isLoading ? (
          <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '40px' }} />
        ) : planError ? (
          <Alert
            message="加载计划失败"
            description={
              <div>
                <p>{planError instanceof Error ? planError.message : '无法加载计划，请稍后重试'}</p>
                <Button
                  type="link"
                  onClick={() => refetch()}
                  style={{ padding: 0, marginTop: 8 }}
                >
                  点击重试
                </Button>
              </div>
            }
            type="error"
            showIcon
            action={
              <Button size="small" onClick={() => refetch()}>
                重试
              </Button>
            }
          />
        ) : planData ? (
          <Tabs items={tabItems} />
        ) : (
          <Alert
            message="暂无计划"
            description="请点击「生成计划」按钮来生成实现计划"
            type="info"
            showIcon
          />
        )}
      </Card>

      <TaskDetailModal
        visible={showDetail}
        task={selectedTask}
        onClose={() => setShowDetail(false)}
      />
    </div>
  )
}

export default PlanningView
