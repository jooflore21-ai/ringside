import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { CssBaseline, ThemeProvider } from '@mui/material'
import App from './App'
import { tema } from './tema'
import { AuthProvider } from './contexts/AuthContext'
import { CarrinhoProvider } from './contexts/CarrinhoContext'

// Providers envolvem o app uma vez; qualquer tela lê usuário e carrinho
// com useAuth() e useCarrinho(), sem passar props de pai para filho.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={tema}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <CarrinhoProvider>
            <App />
          </CarrinhoProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
