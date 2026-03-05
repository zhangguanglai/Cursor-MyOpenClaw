import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/MainLayout'
import ErrorBoundary from './components/ErrorBoundary'
import RequirementCenter from './features/requirement-center/RequirementCenter'
import PlanningView from './features/planning/PlanningView'
import ExecutionView from './features/execution/ExecutionView'
import TestingView from './features/testing/TestingView'
import HistoryView from './features/history/HistoryView'
import KnowledgeView from './features/knowledge/KnowledgeView'

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/cases" replace />} />
          <Route path="/cases" element={<RequirementCenter />} />
                  <Route path="/cases/:caseId/plan" element={<ErrorBoundary><PlanningView /></ErrorBoundary>} />
                  <Route path="/cases/:caseId/execution" element={<ExecutionView />} />
                  <Route path="/cases/:caseId/test" element={<TestingView />} />
                  <Route path="/cases/:caseId/history" element={<HistoryView />} />
                  <Route path="/knowledge" element={<KnowledgeView />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  )
}

export default App
