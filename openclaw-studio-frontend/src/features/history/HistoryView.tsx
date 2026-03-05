import { useState, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { Card, Space, Row, Col, Spin, Alert, Breadcrumb, Typography } from 'antd'
import { HomeOutlined } from '@ant-design/icons'
import { useCaseQuery } from '../../services/cases'
import { useCaseHistoryQuery } from '../../services/history'
import type { HistoryItem } from '../../services/types'
import { HistoryTimeline } from './HistoryTimeline'
import { HistoryFilters } from './HistoryFilters'
import { HistoryStatsCard } from './HistoryStatsCard'
import { HistoryDetailModal } from './HistoryDetailModal'

const { Title } = Typography

const HistoryView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const { data: caseData } = useCaseQuery(caseId || '')
  const [filters, setFilters] = useState({
    types: [] as string[],
    startTime: '',
    endTime: '',
    search: '',
  })
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null)

  // 构建查询参数
  const queryParams = {
    types: filters.types.length > 0 ? filters.types : undefined,
    startTime: filters.startTime || undefined,
    endTime: filters.endTime || undefined,
    search: filters.search || undefined,
  }

  const { data, isLoading, error } = useCaseHistoryQuery(caseId || '', queryParams)
  const history = data?.history || []

  // 计算统计信息
  const stats = useMemo(() => {
    const counts: Record<string, number> = {}
    let totalEvents = history.length

    history.forEach((item) => {
      counts[item.type] = (counts[item.type] || 0) + 1
    })

    return {
      totalEvents,
      counts,
    }
  }, [history])

  // 过滤历史记录
  const filteredHistory = useMemo(() => {
    let result = history

    // 按类型筛选
    if (filters.types.length > 0) {
      result = result.filter((item) => filters.types.includes(item.type))
    }

    // 按时间范围筛选
    if (filters.startTime) {
      const start = new Date(filters.startTime).getTime()
      result = result.filter((item) => new Date(item.timestamp).getTime() >= start)
    }
    if (filters.endTime) {
      const end = new Date(filters.endTime).getTime()
      result = result.filter((item) => new Date(item.timestamp).getTime() <= end)
    }

    // 按搜索关键词筛选
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      result = result.filter(
        (item) =>
          item.description.toLowerCase().includes(searchLower) ||
          JSON.stringify(item.data).toLowerCase().includes(searchLower)
      )
    }

    return result
  }, [history, filters])

  if (error) {
    return (
      <Card title="开发历史时间线">
        <Alert message="加载历史记录失败" description={(error as any)?.message} type="error" showIcon />
      </Card>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card title="开发历史时间线" style={{ marginBottom: 24 }}>
        <HistoryFilters value={filters} onChange={setFilters} />
      </Card>

      <Row gutter={[24, 24]}>
        <Col span={18}>
          <Card>
            {isLoading ? (
              <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '40px' }} />
            ) : filteredHistory.length > 0 ? (
              <HistoryTimeline items={filteredHistory} loading={isLoading} onItemClick={setSelectedItem} />
            ) : (
              <Alert message="暂无历史记录" type="info" showIcon />
            )}
          </Card>
        </Col>
        <Col span={6}>
          <HistoryStatsCard stats={stats} history={history} />
        </Col>
      </Row>

      <HistoryDetailModal open={!!selectedItem} onClose={() => setSelectedItem(null)} item={selectedItem} />
    </div>
  )
}

export default HistoryView
