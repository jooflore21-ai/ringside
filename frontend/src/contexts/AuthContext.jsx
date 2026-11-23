import { createContext, useContext, useMemo, useState } from 'react'

const AuthContext = createContext(null)

// Lê o papel de dentro do JWT só para a interface (mostrar ou esconder menus).
// Quem decide de verdade o acesso é o back-end: 401 sem token, 403 sem permissão.
function lerPayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  const valor = useMemo(() => {
    const payload = token ? lerPayload(token) : null
    return {
      token,
      logado: Boolean(payload),
      ehAdmin: payload?.papel === 'admin',
      entrar(novoToken) {
        localStorage.setItem('token', novoToken)
        setToken(novoToken)
      },
      sair() {
        localStorage.removeItem('token')
        setToken(null)
      },
    }
  }, [token])

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
