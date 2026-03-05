import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Button,
  Card,
  List,
  Tag,
  Collapse,
  Progress,
  Typography,
  Space,
  Alert,
  message,
  Checkbox,
  Select,
} from 'antd'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useGenerateTestMutation, useGetTestResultsQuery } from '../../services/testing'
import type { TestResponseOut } from '../../services/types'

const { Title, Text, Paragraph } = Typography
const { Panel } = Collapse
const { Option } = Select

// Severity tag color mapping
const severityColorMap: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'geekblue',
  low: 'green',
}

// Helper: parse checklist markdown into items and track state
const parseChecklist = (raw: string[]): { text: string; checked: boolean }[] => {
  return raw.map((line) => {
    const match = line.match(/^\s*[-*+]\s*(?:\[([ x])\]\s+)?(.*)$/)
    if (!match) return { text: line, checked: false }
    const [, checkedStr, text] = match
    return {
      text: text.trim(),
      checked: checkedStr?.toLowerCase() === 'x' || checkedStr === 'X',
    }
  })
}

const TestingView = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const [checklistState, setChecklistState] = useState<{ text: string; checked: boolean }[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [severityFilter, setSeverityFilter] = useState<string>('all')

  // Fetch test results
  const { data, isLoading, error, refetch } = useGetTestResultsQuery(caseId || '')

  // Generate mutation
  const generateMutation = useGenerateTestMutation(caseId || '')

  // Initialize checklist from API or localStorage
  useEffect(() => {
    if (data?.checklist || data?.manual_checklist) {
      const checklist = data.checklist || data.manual_checklist || []
      const parsed = parseChecklist(checklist)
      // Try restore from localStorage
      try {
        const saved = localStorage.getItem(`test-checklist-${caseId}`)
        if (saved) {
          const restored = JSON.parse(saved)
          if (Array.isArray(restored) && restored.length === parsed.length) {
            setChecklistState(restored)
            return
          }
        }
      } catch (e) {
        console.warn('Failed to load checklist from localStorage', e)
      }
      setChecklistState(parsed)
    }
  }, [data?.checklist, data?.manual_checklist, caseId])

  // Save to localStorage when changed
  useEffect(() => {
    if (caseId && checklistState.length > 0) {
      try {
        localStorage.setItem(`test-checklist-${caseId}`, JSON.stringify(checklistState))
      } catch (e) {
        console.warn('Failed to save checklist to localStorage', e)
      }
    }
  }, [caseId, checklistState])

  const handleToggleCheck = (index: number) => {
    setChecklistState((prev) =>
      prev.map((item, i) => (i === index ? { ...item, checked: !item.checked } : item))
    )
  }

  const handleSaveChecklist = async () => {
    if (!caseId) return
    setIsSaving(true)
    try {
      // Optional: send to backend via PATCH /cases/{id}/test/checklist
      // For now, just persist in localStorage (per requirement: "可选保存")
      message.success('验收状态已保存')
    } catch (err) {
      message.error('保存失败')
    } finally {
      setIsSaving(false)
    }
  }

  const progress = checklistState.filter((i) => i.checked).length
  const total = checklistState.length
  const progressPercent = total > 0 ? Math.round((progress / total) * 100) : 0

  // Render Markdown with custom components
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
    list({ children, ordered }: any) {
      return ordered ? <ol style={{ paddingLeft: '24px' }}>{children}</ol> : <ul style={{ paddingLeft: '24px' }}>{children}</ul>
    },
  }

  if (isLoading) {
    return (
      <Card title="测试建议" loading>
        <div>加载中...</div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card title="测试建议">
        <Alert message="加载测试结果失败" description={(error as any)?.message} type="error" showIcon />
      </Card>
    )
  }

  if (!data) {
    return (
      <Card
        title="测试建议"
        extra={
          <Button
            type="primary"
            onClick={async () => {
              try {
                await generateMutation.mutateAsync({
                  patches: [],
                  related_files: [],
                })
                message.success('✅ 测试建议生成成功')
                refetch()
              } catch (err) {
                message.error('❌ 生成失败：' + ((err as any)?.message || '未知错误'))
              }
            }}
            loading={generateMutation.isPending}
            disabled={generateMutation.isPending}
          >
            生成测试建议
          </Button>
        }
      >
        <Alert
          message="暂无测试结果"
          description="请先点击「生成测试建议」获取分析结果"
          type="info"
          showIcon
        />
      </Card>
    )
  }

  const { potential_issues = [], test_cases = [], checklist = [], manual_checklist = [], test_id, generated_at } = data
  const finalChecklist = checklist.length > 0 ? checklist : manual_checklist

  // Filter issues by severity
  const filteredIssues = potential_issues.filter(
    (issue) => severityFilter === 'all' || issue.severity === severityFilter
  )

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '16px' }}>
      {/* Header Card */}
      <Card
        title="🧪 测试建议与验收清单"
        extra={
          <Space>
            {generated_at && <Text type="secondary">生成于：{new Date(generated_at).toLocaleString()}</Text>}
            <Button
              type="primary"
              onClick={() => refetch()}
              loading={generateMutation.isPending}
              disabled={generateMutation.isPending}
            >
              刷新
            </Button>
            <Button
              danger
              onClick={async () => {
                try {
                  await generateMutation.mutateAsync({
                    patches: [],
                    related_files: [],
                  })
                  message.success('✅ 测试建议已重新生成')
                  refetch()
                } catch (err) {
                  message.error('❌ 生成失败：' + ((err as any)?.message || '未知错误'))
                }
              }}
              loading={generateMutation.isPending}
              disabled={generateMutation.isPending}
            >
              重新生成
            </Button>
          </Space>
        }
      >
        {/* Potential Issues */}
        <Title level={4} style={{ marginTop: '24px' }}>
          ⚠️ 潜在问题
        </Title>
        <Space style={{ marginBottom: 16 }}>
          <Text strong>筛选：</Text>
          <Select
            value={severityFilter}
            onChange={setSeverityFilter}
            style={{ width: 120 }}
          >
            <Option value="all">全部</Option>
            <Option value="critical">严重</Option>
            <Option value="high">高</Option>
            <Option value="medium">中</Option>
            <Option value="low">低</Option>
          </Select>
        </Space>
        {filteredIssues && filteredIssues.length > 0 ? (
          <List
            itemLayout="horizontal"
            dataSource={filteredIssues}
            renderItem={(issue) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space>
                      <Tag color={severityColorMap[issue.severity] || 'default'}>
                        {issue.severity.toUpperCase()}
                      </Tag>
                      <span>{issue.description}</span>
                    </Space>
                  }
                  description={
                    <Text type="secondary">
                      关联文件：{issue.related_files?.join(', ') || '无'}
                    </Text>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Paragraph type="secondary">暂无识别到潜在问题</Paragraph>
        )}

        {/* Test Cases */}
        <Title level={4} style={{ marginTop: '32px' }}>
          📝 测试用例
        </Title>
        {test_cases && test_cases.length > 0 ? (
          <Collapse defaultActiveKey={['0']} ghost>
            {test_cases.map((tc, idx) => (
              <Panel
                key={idx}
                header={
                  <Space>
                    <Text strong>{tc.description || `测试用例 #${idx + 1}`}</Text>
                    <Tag size="small" color="processing">
                      {tc.steps?.length || 0} 步
                    </Tag>
                  </Space>
                }
              >
                <Paragraph>
                  <strong>步骤：</strong>
                  <ol style={{ paddingLeft: '24px', marginTop: '8px', marginBottom: '16px' }}>
                    {tc.steps?.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                </Paragraph>
                <Paragraph>
                  <strong>预期结果：</strong>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={renderers}
                  >
                    {tc.expected_result || '无'}
                  </ReactMarkdown>
                </Paragraph>
              </Panel>
            ))}
          </Collapse>
        ) : (
          <Paragraph type="secondary">暂无生成测试用例</Paragraph>
        )}

        {/* Checklist */}
        <Title level={4} style={{ marginTop: '32px' }}>
          ✅ 验收清单
        </Title>
        <Progress
          percent={progressPercent}
          status={progressPercent === 100 ? 'success' : 'active'}
          format={() => `${progress}/${total}`}
          style={{ marginBottom: '16px' }}
        />
        {checklistState.length > 0 ? (
          <List
            dataSource={checklistState}
            renderItem={(item, idx) => (
              <List.Item key={idx}>
                <List.Item.Meta
                  avatar={
                    <Checkbox
                      checked={item.checked}
                      onChange={() => handleToggleCheck(idx)}
                    />
                  }
                  title={<Text delete={item.checked}>{item.text}</Text>}
                />
              </List.Item>
            )}
          />
        ) : (
          <Paragraph type="secondary">暂无验收项</Paragraph>
        )}
        <div style={{ marginTop: '24px', textAlign: 'right' }}>
          <Button
            type="primary"
            onClick={handleSaveChecklist}
            loading={isSaving}
            disabled={isSaving}
          >
            保存验收状态
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default TestingView
