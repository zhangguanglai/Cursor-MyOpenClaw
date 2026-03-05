import { useMemo } from 'react'
import { Card, Statistic, Row, Col, Typography } from 'antd'
import type { HistoryItem } from '../../services/types'

const { Title } = Typography

interface Props {
  stats: {
    totalEvents: number
    counts: Record<string, number>
  }
  history: HistoryItem[]
}

const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
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

export const HistoryStatsCard = ({ stats, history }: Props) => {
  // 计算时间范围
  const timeRange = useMemo(() => {
    if (history.length === 0) return null
    const timestamps = history.map((item) => new Date(item.timestamp).getTime())
    const minTime = Math.min(...timestamps)
    const maxTime = Math.max(...timestamps)
    const duration = maxTime - minTime
    const days = Math.floor(duration / (1000 * 60 * 60 * 24))
    const hours = Math.floor((duration % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    return { days, hours }
  }, [history])

  return (
    <Card title="统计信息">
      <Statistic title="总事件数" value={stats.totalEvents} />
      <div style={{ marginTop: 24 }}>
        <Title level={5}>事件类型分布</Title>
        <Row gutter={[16, 16]}>
          {Object.entries(stats.counts).map(([type, count]) => (
            <Col span={12} key={type}>
              <Statistic title={getTypeLabel(type)} value={count} />
            </Col>
          ))}
        </Row>
      </div>
      {timeRange && (
        <div style={{ marginTop: 24 }}>
          <Title level={5}>开发时长</Title>
          <Statistic title="总时长" value={`${timeRange.days} 天 ${timeRange.hours} 小时`} />
        </div>
      )}
    </Card>
  )
}
