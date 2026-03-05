import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Alert, Button } from 'antd'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error,
      errorInfo,
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div style={{ padding: '24px' }}>
          <Alert
            message="页面渲染出错"
            description={
              <div>
                <p>{this.state.error?.message || '未知错误'}</p>
                {this.state.errorInfo && (
                  <details style={{ marginTop: 16 }}>
                    <summary>错误详情</summary>
                    <pre style={{ marginTop: 8, fontSize: '12px', overflow: 'auto' }}>
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            }
            type="error"
            showIcon
            action={
              <Button size="small" onClick={this.handleReset}>
                重试
              </Button>
            }
          />
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
