import { Modal, Typography, Divider, Tag, Descriptions } from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { HistoryItem } from '../../services/types'

const { Title, Text, Paragraph } = Typography

interface Props {
  open: boolean
  onClose: () => void
  item: HistoryItem | null
}

const renderers = {
  code({ node, inline, className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className || '')
    return !inline && match ? (
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={match[1]}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    ) : (
      <code className={className} {...props}>
        {children}
      </code>
    )
  },
}

export const HistoryDetailModal = ({ open, onClose, item }: Props) => {
  if (!item) return null

  const renderContent = () => {
    switch (item.type) {
      case 'case':
        return (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="案例 ID">{item.data.id}</Descriptions.Item>
            <Descriptions.Item label="标题">{item.data.title}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={item.data.status === 'completed' ? 'success' : 'processing'}>{item.data.status}</Tag>
            </Descriptions.Item>
          </Descriptions>
        )

      case 'plan':
        return (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="计划 ID">{item.data.plan_id}</Descriptions.Item>
            <Descriptions.Item label="任务数">{item.data.tasks_count}</Descriptions.Item>
          </Descriptions>
        )

      case 'patch':
        return (
          <>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="任务 ID">{item.data.task_id}</Descriptions.Item>
              <Descriptions.Item label="文件路径">
                <Text code>{item.data.file_path}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="描述">{item.data.description}</Descriptions.Item>
            </Descriptions>
            {item.data.patch_content && (
              <>
                <Divider />
                <Title level={5}>补丁内容</Title>
                <pre
                  style={{
                    overflowX: 'auto',
                    backgroundColor: '#2d2d2d',
                    padding: '12px',
                    borderRadius: '4px',
                    color: '#fff',
                  }}
                >
                  <code>{item.data.patch_content}</code>
                </pre>
              </>
            )}
          </>
        )

      case 'agent_run':
        return (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="Agent 类型">
              <Tag color="blue">{item.data.agent_type}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="模型">{item.data.model || 'N/A'}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={item.data.status === 'completed' ? 'success' : 'processing'}>{item.data.status}</Tag>
            </Descriptions.Item>
          </Descriptions>
        )

      case 'test':
        return (
          <>
            {item.data.potential_issues && item.data.potential_issues.length > 0 && (
              <>
                <Title level={5}>潜在问题</Title>
                <ul>
                  {item.data.potential_issues.map((issue: any, idx: number) => (
                    <li key={idx}>
                      <Tag color={issue.severity === 'high' ? 'red' : 'orange'}>{issue.severity}</Tag>
                      {issue.description}
                    </li>
                  ))}
                </ul>
                <Divider />
              </>
            )}
            {item.data.test_cases && item.data.test_cases.length > 0 && (
              <>
                <Title level={5}>测试用例</Title>
                {item.data.test_cases.map((tc: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: 16 }}>
                    <Text strong>{tc.description}</Text>
                    {tc.steps && (
                      <ol>
                        {tc.steps.map((step: string, stepIdx: number) => (
                          <li key={stepIdx}>{step}</li>
                        ))}
                      </ol>
                    )}
                  </div>
                ))}
              </>
            )}
          </>
        )

      default:
        return (
          <pre style={{ overflowX: 'auto', backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
            {JSON.stringify(item.data, null, 2)}
          </pre>
        )
    }
  }

  return (
    <Modal
      title={`事件详情 - ${item.description}`}
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      style={{ top: 20 }}
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">时间: {new Date(item.timestamp).toLocaleString()}</Text>
      </div>
      <Divider />
      {renderContent()}
    </Modal>
  )
}
