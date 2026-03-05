import { useState } from 'react'
import { Button, Table, Drawer, Form, Input, Space, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { useCasesQuery, useCreateCaseMutation } from '../../services/cases'
import type { CaseCreate } from '../../services/types'

const RequirementCenter = () => {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [form] = Form.useForm()
  
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

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
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
