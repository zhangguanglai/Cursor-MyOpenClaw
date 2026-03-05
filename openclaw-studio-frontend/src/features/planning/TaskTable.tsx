import React, { useState, useMemo } from 'react'
import { Table, Tag, Badge, Modal, Typography, Space, Button, Select, Tooltip } from 'antd'
import { EditOutlined, FileTextOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { TaskOut } from '../../services/types'

const { Text } = Typography

interface TaskTableProps {
  tasks: TaskOut[]
  onStatusChange: (id: string, status: 'pending' | 'completed') => void
  onTaskClick: (task: TaskOut) => void
}

export const TaskTable: React.FC<TaskTableProps> = ({
  tasks,
  onStatusChange,
  onTaskClick,
}) => {
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'completed'>('all')
  const [sortField, setSortField] = useState<'title' | 'risk_level'>('title')
  const [sortOrder, setSortOrder] = useState<'ascend' | 'descend'>('ascend')

  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => filterStatus === 'all' || t.status === filterStatus)
  }, [tasks, filterStatus])

  const sortedTasks = useMemo(() => {
    return [...filteredTasks].sort((a, b) => {
      const aValue = a[sortField]
      const bValue = b[sortField]
      if (sortOrder === 'ascend') {
        return String(aValue).localeCompare(String(bValue))
      } else {
        return String(bValue).localeCompare(String(aValue))
      }
    })
  }, [filteredTasks, sortField, sortOrder])

  const columns: ColumnsType<TaskOut> = [
    {
      title: '状态',
      key: 'status',
      width: 120,
      render: (_, record) => (
        <Badge
          status={record.status === 'completed' ? 'success' : 'processing'}
          text={record.status === 'completed' ? '已完成' : '待处理'}
        />
      ),
      filterDropdown: () => (
        <div style={{ padding: 8 }}>
          <Select
            value={filterStatus}
            onChange={(v) => setFilterStatus(v as any)}
            style={{ width: 120 }}
          >
            <Select.Option value="all">全部</Select.Option>
            <Select.Option value="pending">待处理</Select.Option>
            <Select.Option value="completed">已完成</Select.Option>
          </Select>
        </div>
      ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      sorter: true,
      onHeaderCell: () => ({
        onClick: () => {
          setSortField('title')
          setSortOrder(sortOrder === 'ascend' ? 'descend' : 'ascend')
        },
      }),
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      width: 120,
      render: (level) => (
        <Tag color={level === 'high' ? 'error' : level === 'medium' ? 'warning' : 'success'}>
          {level === 'high' ? '高' : level === 'medium' ? '中' : '低'}
        </Tag>
      ),
      filters: [
        { text: '高', value: 'high' },
        { text: '中', value: 'medium' },
        { text: '低', value: 'low' },
      ],
      onFilter: (value, record) => record.risk_level === value,
      sorter: true,
      onHeaderCell: () => ({
        onClick: () => {
          setSortField('risk_level')
          setSortOrder(sortOrder === 'ascend' ? 'descend' : 'ascend')
        },
      }),
    },
    {
      title: '关联文件',
      dataIndex: 'related_files',
      key: 'related_files',
      width: 120,
      render: (files: string[]) =>
        files && files.length > 0 ? (
          <Tooltip title={files.join(', ')}>
            <Text type="secondary">{files.length} 个</Text>
          </Tooltip>
        ) : (
          <Text type="secondary">无</Text>
        ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => onStatusChange(record.id, record.status === 'pending' ? 'completed' : 'pending')}
          >
            {record.status === 'pending' ? '标记完成' : '标记待办'}
          </Button>
          <Button
            type="link"
            icon={<FileTextOutlined />}
            onClick={() => onTaskClick(record)}
          >
            查看详情
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <Table
      columns={columns}
      dataSource={sortedTasks}
      rowKey="id"
      pagination={{ pageSize: 10 }}
      scroll={{ y: 300 }}
      size="small"
    />
  )
}

// 任务详情 Modal
export const TaskDetailModal: React.FC<{
  visible: boolean
  task: TaskOut | null
  onClose: () => void
}> = ({ visible, task, onClose }) => {
  if (!task) return null

  return (
    <Modal
      title={`任务详情：${task.title}`}
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>,
      ]}
      width={720}
    >
      <p>
        <strong>描述：</strong>
        {task.description}
      </p>
      <p>
        <strong>风险等级：</strong>
        <Tag color={task.risk_level === 'high' ? 'error' : task.risk_level === 'medium' ? 'warning' : 'success'}>
          {task.risk_level === 'high' ? '高' : task.risk_level === 'medium' ? '中' : '低'}
        </Tag>
      </p>
      <p>
        <strong>状态：</strong>
        <Badge
          status={task.status === 'completed' ? 'success' : 'processing'}
          text={task.status === 'completed' ? '已完成' : '待处理'}
        />
      </p>
      <p>
        <strong>关联文件：</strong>
        {task.related_files && task.related_files.length > 0 ? (
          <ul>
            {task.related_files.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        ) : (
          <Text type="secondary">无</Text>
        )}
      </p>
    </Modal>
  )
}
