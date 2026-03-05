import { useParams } from 'react-router-dom'
import { Card, List, Typography } from 'antd'
import { useCasePatchesQuery } from '../../services/coding'

const { Text } = Typography

const ExecutionView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const { data: patches, isLoading } = useCasePatchesQuery(caseId || '')

  return (
    <div>
      <Card title="代码补丁">
        {isLoading ? (
          <div>加载中...</div>
        ) : patches && patches.length > 0 ? (
          <List
            dataSource={patches}
            renderItem={(patch) => (
              <List.Item>
                <div>
                  <Text strong>{patch.file_path}</Text>
                  <div style={{ marginTop: 8 }}>
                    <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '12px' }}>
                      {patch.content}
                    </pre>
                  </div>
                </div>
              </List.Item>
            )}
          />
        ) : (
          <div>暂无补丁</div>
        )}
      </Card>
    </div>
  )
}

export default ExecutionView
