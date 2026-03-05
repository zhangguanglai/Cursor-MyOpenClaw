import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import MainLayout from './components/MainLayout'
import RequirementCenter from './features/requirement-center/RequirementCenter'
import PlanningView from './features/planning/PlanningView'
import ExecutionView from './features/execution/ExecutionView'
import TestingView from './features/testing/TestingView'
import HistoryView from './features/history/HistoryView'

const { Content } = Layout

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Content style={{ padding: '24px', minHeight: '100vh' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/cases" replace />} />
            <Route path="/cases" element={<RequirementCenter />} />
            <Route path="/cases/:caseId/plan" element={<PlanningView />} />
            <Route path="/cases/:caseId/execution" element={<ExecutionView />} />
            <Route path="/cases/:caseId/test" element={<TestingView />} />
            <Route path="/cases/:caseId/history" element={<HistoryView />} />
          </Routes>
        </Content>
      </MainLayout>
    </BrowserRouter>
  )
}

export default App
