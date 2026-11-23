import { Alert, Box, CircularProgress, Typography } from '@mui/material'

// Componente reutilizável para os três estados que o trabalho exige em toda tela:
// carregando, erro e lista vazia.
export default function EstadoRequisicao({ carregando, erro, vazio, mensagemVazio = 'Nada por aqui.', children }) {
  if (carregando) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }} role="status" aria-live="polite">
        <CircularProgress aria-label="Carregando" />
      </Box>
    )
  }
  if (erro) return <Alert severity="error" role="alert">{erro}</Alert>
  if (vazio) return <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>{mensagemVazio}</Typography>
  return children
}
