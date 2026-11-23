import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import RotaProtegida from './components/RotaProtegida'
import Inicio from './pages/Inicio'
import EmConstrucao from './pages/EmConstrucao'

// As 6 telas mínimas do trabalho já têm rota; cada uma ganha conteúdo nas próximas etapas.
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Inicio />} />
        <Route path="produtos/:id" element={<EmConstrucao titulo="Detalhe do produto" />} />
        <Route path="carrinho" element={<EmConstrucao titulo="Carrinho" />} />
        <Route path="login" element={<EmConstrucao titulo="Entrar" />} />
        <Route path="cadastro" element={<EmConstrucao titulo="Criar conta" />} />

        <Route element={<RotaProtegida />}>
          <Route path="meus-pedidos" element={<EmConstrucao titulo="Meus pedidos" />} />
        </Route>

        <Route path="admin" element={<RotaProtegida somenteAdmin />}>
          <Route index element={<EmConstrucao titulo="Área administrativa" />} />
        </Route>

        <Route path="*" element={<EmConstrucao titulo="Página não encontrada" />} />
      </Route>
    </Routes>
  )
}
