import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface PlanRendererProps {
  markdown: string
}

export const PlanRenderer: React.FC<PlanRendererProps> = ({ markdown }) => {
  return (
    <div
      style={{
        padding: '16px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        border: '1px solid #f0f0f0',
        overflowY: 'auto',
        maxHeight: '50vh',
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
        {markdown}
      </ReactMarkdown>
    </div>
  )
}
