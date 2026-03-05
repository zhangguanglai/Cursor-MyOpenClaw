import React, { useState, useEffect } from 'react'
import { Button, Space, message } from 'antd'
import { EditOutlined, EyeOutlined, SaveOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface MarkdownEditorProps {
  markdown: string
  onSave: (content: string) => Promise<void>
  isSaving?: boolean
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  markdown,
  onSave,
  isSaving = false,
}) => {
  const [value, setValue] = useState(markdown)
  const [mode, setMode] = useState<'edit' | 'preview'>('edit')

  useEffect(() => {
    setValue(markdown)
  }, [markdown])

  const handleSave = async () => {
    try {
      await onSave(value)
      message.success('计划保存成功')
    } catch (error) {
      message.error('计划保存失败')
    }
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Space direction="horizontal" style={{ marginBottom: 16 }}>
        <Button
          type={mode === 'edit' ? 'primary' : 'default'}
          icon={<EditOutlined />}
          onClick={() => setMode('edit')}
        >
          编辑
        </Button>
        <Button
          type={mode === 'preview' ? 'primary' : 'default'}
          icon={<EyeOutlined />}
          onClick={() => setMode('preview')}
        >
          预览
        </Button>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          loading={isSaving}
          onClick={handleSave}
        >
          保存计划
        </Button>
      </Space>

      {mode === 'edit' ? (
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          style={{
            flex: 1,
            width: '100%',
            padding: '12px',
            fontFamily: 'monospace',
            fontSize: '14px',
            border: '1px solid #d9d9d9',
            borderRadius: '6px',
            resize: 'none',
          }}
        />
      ) : (
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '12px',
            backgroundColor: '#fff',
            borderRadius: '6px',
            border: '1px solid #f0f0f0',
          }}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
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
              table: ({ children }) => (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>{children}</table>
                </div>
              ),
              th: ({ children }) => (
                <th
                  style={{
                    border: '1px solid #ddd',
                    padding: '8px 12px',
                    textAlign: 'left',
                    backgroundColor: '#f9f9f9',
                    fontWeight: 'bold',
                  }}
                >
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td
                  style={{
                    border: '1px solid #ddd',
                    padding: '8px 12px',
                    textAlign: 'left',
                  }}
                >
                  {children}
                </td>
              ),
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: '#1890ff' }}>
                  {children}
                </a>
              ),
              img: ({ src, alt }) => (
                <img
                  src={src}
                  alt={alt}
                  style={{ maxWidth: '100%', height: 'auto', borderRadius: '4px' }}
                />
              ),
            }}
          >
            {value}
          </ReactMarkdown>
        </div>
      )}
    </div>
  )
}
