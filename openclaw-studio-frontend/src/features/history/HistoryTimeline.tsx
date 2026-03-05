import { Timeline, Tag, Tooltip } from 'antd'
import type { HistoryItem, HistoryItemType } from '../../services/types'

interface Props {
  items: HistoryItem[]
  loading: boolean
  onItemClick: (item: HistoryItem) => void
}

const getDotColor = (type: HistoryItemType): string => {
  switch (type) {
    case 'case':
      return '#1890ff'
    case 'plan':
      return '#52c41a'
    case 'task':
      return '#faad14'
    case 'patch':
      return '#eb2f96'
    case 'test':
      return '#722ed1'
    case 'agent_run':
      return '#13c2c2'
    default:
      return '#bfbfbf'
  }
}

const getTypeLabel = (type: HistoryItemType): string => {
  const labels: Record<HistoryItemType, string> = {
    case: '案例',
    plan: '规划',
    task: '任务',
    patch: '补丁',
    test: '测试',
    agent_run: 'Agent',
    summary: '总结',
  }
  return labels[type] || type
}

export const HistoryTimeline = ({ items, loading, onItemClick }: Props) => {
  return (
    <Timeline pending={loading ? '加载中...' : undefined}>
      {items.map((item, index) => (
        <Timeline.Item
          key={item.id || `${item.type}-${item.timestamp}-${index}`}
          color={getDotColor(item.type)}
          dot={
            <Tooltip title={getTypeLabel(item.type)}>
              <Tag color={getDotColor(item.type)} style={{ cursor: 'pointer' }}>
                {getTypeLabel(item.type)}
              </Tag>
            </Tooltip>
          }
        >
          <div
            style={{ cursor: 'pointer', padding: '8px', borderRadius: '4px', transition: 'background-color 0.2s' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f5f5f5'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent'
            }}
            onClick={() => onItemClick(item)}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{item.description}</div>
            <div style={{ fontSize: '12px', color: '#999', marginTop: 4 }}>
              {new Date(item.timestamp).toLocaleString()}
            </div>
            {item.type === 'patch' && 'data' in item && 'file_path' in item.data && (
              <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                文件: {item.data.file_path}
              </div>
            )}
            {item.type === 'plan' && 'data' in item && 'tasks_count' in item.data && (
              <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                任务数: {item.data.tasks_count}
              </div>
            )}
            {item.type === 'agent_run' && 'data' in item && 'agent_type' in item.data && (
              <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                Agent: {item.data.agent_type} | 模型: {item.data.model || 'N/A'}
              </div>
            )}
          </div>
        </Timeline.Item>
      ))}
    </Timeline>
  )
}
