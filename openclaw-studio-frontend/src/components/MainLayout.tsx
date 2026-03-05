import type { ReactNode } from 'react'
import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  FileTextOutlined,
  UnorderedListOutlined,
  CodeOutlined,
  CheckCircleOutlined,
  HistoryOutlined,
  BookOutlined,
} from '@ant-design/icons'

const { Header, Sider } = Layout

interface MainLayoutProps {
  children: ReactNode
}

const MainLayout = ({ children }: MainLayoutProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/cases',
      icon: <FileTextOutlined />,
      label: '需求中心',
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ color: '#fff', fontSize: '20px', fontWeight: 'bold' }}>
          OpenClaw Studio
        </div>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname.split('/').slice(0, 2).join('/')]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Layout.Content style={{ padding: '24px', minHeight: '100vh' }}>
          {children}
        </Layout.Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
