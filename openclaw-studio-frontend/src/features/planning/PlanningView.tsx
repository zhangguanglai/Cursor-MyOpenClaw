import { useParams, useNavigate } from 'react-router-dom'
import { Button, Card, Tabs, message, Spin, Alert, Breadcrumb, Typography } from 'antd'
import { SyncOutlined, HomeOutlined } from '@ant-design/icons'
import { useState, useEffect } from 'react'
import { useCasePlanQuery, useTriggerPlanningMutation, useUpdatePlanMutation, useUpdateTaskStatusMutation } from '../../services/planning'
import { useCaseQuery } from '../../services/cases'
import type { TaskOut } from '../../services/types'
import { MarkdownEditor } from '../../components/MarkdownEditor'
import { TaskTable, TaskDetailModal } from './TaskTable'
import { PlanRenderer } from './PlanRenderer'

const { Title } = Typography

const PlanningView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const { data: caseData } = useCaseQuery(caseId || '')
  const { data: planData, isLoading, refetch } = useCasePlanQuery(caseId || '')
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
      setEditingMarkdown(planData.plan_markdown)
      setTasks(
        planData.tasks.map((t) => ({
          ...t,
          status: (t.status as 'pending' | 'completed') || 'pending',
        }))
      )
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
      message.error('规划生成失败')
    }
  }

  const handleSavePlan = async (content: string) => {
    await updateMutation.mutateAsync(content)
    setIsEditing(false)
  }

  const handleTaskStatusChange = async (taskId: string, status: 'pending' | 'completed') => {
    try {
      await updateTaskStatusMutation.mutateAsync({ taskId, status })
      setTasks(tasks.map(t => t.id === taskId ? { ...t, status } : t))
      message.success('任务状态更新成功')
    } catch (error) {
      message.error('任务状态更新失败')
    }
  }

  const handleTaskClick = (task: TaskOut) => {
    setSelectedTask(task)
    setShowDetail(true)
  }

  const tabItems = [
    {
      key: 'plan',
      label: '计划',
      children: planData ? (
        <div style={{ minHeight: '400px' }}>
          <MarkdownEditor
            markdown={editingMarkdown}
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
  ]

  return (
    <div>
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
      {caseData && (
        <Card style={{ marginBottom: 16 }}>
          <Title level={4}>{caseData.title}</Title>
          <p style={{ color: '#666', marginBottom: 0 }}>{caseData.description}</p>
        </Card>
      )}
      <Card
        title="实现计划"
        extra={
          <Button
            type="primary"
            icon={<SyncOutlined />}
            onClick={handleTriggerPlanning}
            loading={triggerMutation.isPending}
          >
            生成计划
          </Button>
        }
      >
        {isLoading ? (
          <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '40px' }} />
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
