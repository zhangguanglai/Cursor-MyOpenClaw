import { useParams } from 'react-router-dom'
import { Button, Card, message } from 'antd'
import { useGenerateTestMutation } from '../../services/testing'

const TestingView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const generateMutation = useGenerateTestMutation(caseId || '')

  const handleGenerateTest = async () => {
    try {
      await generateMutation.mutateAsync({
        patches: [],
        related_files: [],
      })
      message.success('测试建议生成成功')
    } catch (error) {
      message.error('测试建议生成失败')
    }
  }

  return (
    <div>
      <Card
        title="测试建议"
        extra={
          <Button
            type="primary"
            onClick={handleGenerateTest}
            loading={generateMutation.isPending}
          >
            生成测试建议
          </Button>
        }
      >
        <div>测试视图内容待实现</div>
      </Card>
    </div>
  )
}

export default TestingView
