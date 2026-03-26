import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { CreatePassportPage } from './pages/CreatePassportPage'
import { DashboardPage } from './pages/DashboardPage'
import { LandingPage } from './pages/LandingPage'
import { LineagePage } from './pages/LineagePage'
import { NotFoundPage } from './pages/NotFoundPage'
import { PassportDetailPage } from './pages/PassportDetailPage'
import { PassportListPage } from './pages/PassportListPage'
import { VerifyPassportPage } from './pages/VerifyPassportPage'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<LandingPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="passports" element={<PassportListPage />} />
        <Route path="passports/create" element={<CreatePassportPage />} />
        <Route path="passports/:passportSlug" element={<PassportDetailPage />} />
        <Route path="verify" element={<VerifyPassportPage />} />
        <Route path="lineage" element={<LineagePage />} />
        <Route path="home" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App
