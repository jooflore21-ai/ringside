import { Typography } from '@mui/material'

export default function EmConstrucao({ titulo }) {
  return (
    <>
      <Typography variant="h4" component="h1" gutterBottom>{titulo}</Typography>
      <Typography color="text.secondary">Tela em construção.</Typography>
    </>
  )
}
