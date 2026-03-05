import { useParams } from 'react-router-dom'
import { Button, Card, message } from 'antd'
import { useCasePlanQuery, useTriggerPlanningMutation } from '../../services/planning'
import { useCaseQuery } from '../../services/cases'

const PlanningView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const { data: caseData } = useCaseQuery(caseId || '')
  const { data: planData, isLoading } = useCasePlanQuery(caseId || '')
  const triggerMutation = useTriggerPlanningMutation(caseId || '')

  const handleTriggerPlanning = async () => {
    if (!caseData) return
    
    try {
      await triggerMutation.mutateAsync({
        requirement_description: caseData.description,
        related_files: [],
      })
      message.success('规划生成成功')
    } catch (error) {
      message.error('规划生成失败')
    }
  }

  return (
    <div>
      <Card
        title="实现计划"
        extra={
          <Button
            type="primary"
            onClick={handleTriggerPlanning}
            loading={triggerMutation.isPending}
          >
            生成计划
          </Button>
        }
      >
        {isLoading ? (
          <div>加载中...</div>
        ) : planData ? (
          <div>
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
              {planData.plan_markdown}
            </pre>
          </div>
        ) : (
          <div>暂无计划，请点击"生成计划"按钮</div>
        )}
      </Card>
    </div>
  )
}

export default PlanningView
