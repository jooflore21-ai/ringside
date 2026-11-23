import { useEffect, useState } from 'react'
import { Chip, Stack, Typography } from '@mui/material'
import { api, mensagemDeErro } from '../api/cliente'
import EstadoRequisicao from '../components/EstadoRequisicao'

// Tela provisória: confirma que front, API e banco conversam.
// Vira o catálogo (RF05) na próxima etapa.
export default function Inicio() {
  const [status, setStatus] = useState(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    api.get('/saude')
      .then((r) => setStatus(r.data))
      .catch((e) => setErro(mensagemDeErro(e)))
      .finally(() => setCarregando(false))
  }, [])

  return (
    <Stack spacing={2}>
      <Typography variant="h2" component="h1">Ringside</Typography>
      <Typography color="text.secondary">Ingressos e merch da promoção.</Typography>
      <EstadoRequisicao carregando={carregando} erro={erro}>
        <Stack direction="row" spacing={1}>
          <Chip color="success" label={`API: ${status?.api}`} />
          <Chip color="success" label={`Banco: ${status?.banco}`} />
        </Stack>
      </EstadoRequisicao>
    </Stack>
  )
}
