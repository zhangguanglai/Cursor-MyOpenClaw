import { useParams } from 'react-router-dom'
import { Timeline, Card } from 'antd'
import { useCaseHistoryQuery } from '../../services/history'

const HistoryView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const { data: history, isLoading } = useCaseHistoryQuery(caseId || '')

  const timelineItems = history?.map((item) => ({
    children: (
      <div>
        <div style={{ fontWeight: 'bold' }}>{item.description}</div>
        <div style={{ fontSize: '12px', color: '#999', marginTop: 4 }}>
          {new Date(item.timestamp).toLocaleString()}
        </div>
      </div>
    ),
  })) || []

  return (
    <div>
      <Card title="历史记录">
        {isLoading ? (
          <div>加载中...</div>
        ) : timelineItems.length > 0 ? (
          <Timeline items={timelineItems} />
        ) : (
          <div>暂无历史记录</div>
        )}
      </Card>
    </div>
  )
}

export default HistoryView
