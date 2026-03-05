import { Space, Select, DatePicker, Input } from 'antd'
import type { HistoryItemType } from '../../services/types'

const { Option } = Select
const { RangePicker } = DatePicker

interface Props {
  value: {
    types: string[]
    startTime: string
    endTime: string
    search: string
  }
  onChange: (filters: { types: string[]; startTime: string; endTime: string; search: string }) => void
}

const eventTypes: { value: HistoryItemType; label: string }[] = [
  { value: 'case', label: '案例' },
  { value: 'plan', label: '规划' },
  { value: 'task', label: '任务' },
  { value: 'patch', label: '补丁' },
  { value: 'test', label: '测试' },
  { value: 'agent_run', label: 'Agent' },
  { value: 'summary', label: '总结' },
]

export const HistoryFilters = ({ value, onChange }: Props) => {
  const handleTypesChange = (types: string[]) => {
    onChange({ ...value, types })
  }

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      onChange({
        ...value,
        startTime: dates[0].toISOString(),
        endTime: dates[1].toISOString(),
      })
    } else {
      onChange({
        ...value,
        startTime: '',
        endTime: '',
      })
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...value, search: e.target.value })
  }

  return (
    <Space wrap>
      <Select
        mode="multiple"
        placeholder="筛选事件类型"
        style={{ width: 200 }}
        value={value.types}
        onChange={handleTypesChange}
        allowClear
      >
        {eventTypes.map((type) => (
          <Option key={type.value} value={type.value}>
            {type.label}
          </Option>
        ))}
      </Select>
      <RangePicker
        placeholder={['开始时间', '结束时间']}
        onChange={handleDateRangeChange}
        showTime
        format="YYYY-MM-DD HH:mm:ss"
      />
      <Input.Search
        placeholder="搜索事件描述"
        allowClear
        style={{ width: 300 }}
        value={value.search}
        onChange={handleSearchChange}
      />
    </Space>
  )
}
