import React, { useState } from 'react'
import { Card, Radio, Button, Tooltip } from 'antd'
import { CopyOutlined } from '@ant-design/icons'
import { Diff, parseDiff } from 'react-diff-view'
import 'react-diff-view/style/index.css'

type DiffMode = 'split' | 'unified'

interface DiffPreviewProps {
  patchContent: string
  fileName?: string
}

const DiffPreview: React.FC<DiffPreviewProps> = ({ patchContent, fileName }) => {
  const [mode, setMode] = useState<DiffMode>('split')

  // 解析 patch 内容
  const files = parseDiff(patchContent)

  const handleCopy = () => {
    navigator.clipboard.writeText(patchContent)
  }

  return (
    <Card
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Diff 预览 — {fileName || 'unknown'}</span>
          <Radio.Group value={mode} onChange={(e) => setMode(e.target.value as DiffMode)}>
            <Radio.Button value="split">并排</Radio.Button>
            <Radio.Button value="unified">统一</Radio.Button>
          </Radio.Group>
        </div>
      }
      extra={
        <Tooltip title="复制补丁内容">
          <Button size="small" icon={<CopyOutlined />} onClick={handleCopy}>
            复制
          </Button>
        </Tooltip>
      }
      style={{ marginTop: 16 }}
    >
      <div style={{ maxHeight: 500, overflow: 'auto', fontFamily: 'monospace', fontSize: '12px' }}>
        {files.map((file, index) => (
          <Diff
            key={index}
            viewType={mode}
            diffType={file.type}
            hunks={file.hunks}
            oldPath={file.oldPath}
            newPath={file.newPath}
          />
        ))}
      </div>
    </Card>
  )
}

export default DiffPreview
