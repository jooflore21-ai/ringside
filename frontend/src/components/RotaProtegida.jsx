import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

// Proteção no front é só experiência de uso. A segurança real está no back-end.
export default function RotaProtegida({ somenteAdmin = false }) {
  const { logado, ehAdmin } = useAuth()
  if (!logado) return <Navigate to="/login" replace />
  if (somenteAdmin && !ehAdmin) return <Navigate to="/" replace />
  return <Outlet />
}
