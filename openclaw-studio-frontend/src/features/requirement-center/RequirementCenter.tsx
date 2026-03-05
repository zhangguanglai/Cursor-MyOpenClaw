import { useState } from 'react'
import { Button, Table, Drawer, Form, Input, Space, message, Tag, Dropdown } from 'antd'
import { PlusOutlined, EyeOutlined, UnorderedListOutlined, CodeOutlined, CheckCircleOutlined, HistoryOutlined } from '@ant-design/icons'
import type { MenuProps } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useCasesQuery, useCreateCaseMutation } from '../../services/cases'
import type { CaseCreate, CaseOut } from '../../services/types'

const RequirementCenter = () => {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  
  const { data: cases, isLoading } = useCasesQuery()
  const createMutation = useCreateCaseMutation()

  const handleCreate = async (values: CaseCreate) => {
    try {
      await createMutation.mutateAsync(values)
      message.success('案例创建成功')
      setDrawerOpen(false)
      form.resetFields()
    } catch (error) {
      message.error('案例创建失败')
    }
  }

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      created: 'default',
      planning: 'processing',
      coding: 'processing',
      testing: 'warning',
      completed: 'success',
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
      created: '已创建',
      planning: '规划中',
      coding: '编码中',
      testing: '测试中',
      completed: '已完成',
    }
    return textMap[status] || status
  }

  const handleViewCase = (caseItem: CaseOut) => {
    // 跳转到规划视图（默认）
    navigate(`/cases/${caseItem.id}/plan`)
  }

  const getActionMenu = (caseItem: CaseOut): MenuProps => ({
    items: [
      {
        key: 'plan',
        label: '规划视图',
        icon: <UnorderedListOutlined />,
        onClick: () => navigate(`/cases/${caseItem.id}/plan`),
      },
      {
        key: 'execution',
        label: '执行视图',
        icon: <CodeOutlined />,
        onClick: () => navigate(`/cases/${caseItem.id}/execution`),
      },
      {
        key: 'test',
        label: '测试视图',
        icon: <CheckCircleOutlined />,
        onClick: () => navigate(`/cases/${caseItem.id}/test`),
      },
      {
        key: 'history',
        label: '历史视图',
        icon: <HistoryOutlined />,
        onClick: () => navigate(`/cases/${caseItem.id}/history`),
      },
    ],
  })

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id: string) => <code style={{ fontSize: '12px' }}>{id}</code>,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: CaseOut) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewCase(record)}
          >
            查看详情
          </Button>
          <Dropdown menu={getActionMenu(record)} trigger={['click']}>
            <Button type="link">更多</Button>
          </Dropdown>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setDrawerOpen(true)}
        >
          创建案例
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={cases || []}
        loading={isLoading}
        rowKey="id"
      />

      <Drawer
        title="创建案例"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
        >
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入案例标题" />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <Input.TextArea rows={6} placeholder="请输入需求描述" />
          </Form.Item>
          <Form.Item name="repo_path" label="仓库路径">
            <Input placeholder="可选：Git 仓库路径" />
          </Form.Item>
          <Form.Item name="branch" label="分支">
            <Input placeholder="可选：Git 分支" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                创建
              </Button>
              <Button onClick={() => setDrawerOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}

export default RequirementCenter
