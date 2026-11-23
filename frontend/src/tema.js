import { createTheme } from '@mui/material/styles'

// Identidade visual do nicho: escuro como arena, vermelho de ringue, dourado de cinturão.
export const tema = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#D32F2F' },
    secondary: { main: '#FFC107' },
    background: { default: '#121212', paper: '#1E1E1E' },
  },
  typography: {
    fontFamily: '"Roboto", "Arial", sans-serif',
    h1: { fontWeight: 800, letterSpacing: 1 },
    h2: { fontWeight: 800, letterSpacing: 1 },
  },
  shape: { borderRadius: 8 },
})
