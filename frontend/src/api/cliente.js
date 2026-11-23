import axios from 'axios'

// Uma única instância do Axios para o app inteiro.
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

// Anexa o JWT em toda requisição, se o usuário estiver logado.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Transforma o Problem Details (RFC 9457) da API numa mensagem para a tela.
export function mensagemDeErro(erro) {
  const corpo = erro?.response?.data
  if (corpo?.detail) return corpo.detail
  if (erro?.request && !erro?.response) return 'Não foi possível falar com o servidor.'
  return 'Algo deu errado. Tente novamente.'
}
