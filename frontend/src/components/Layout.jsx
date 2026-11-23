import { AppBar, Badge, Box, Button, Container, IconButton, Toolbar, Typography } from '@mui/material'
import ShoppingCartOutlined from '@mui/icons-material/ShoppingCartOutlined'
import { Link as RouterLink, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useCarrinho } from '../contexts/CarrinhoContext'

export default function Layout() {
  const { logado, ehAdmin, sair } = useAuth()
  const { quantidadeTotal } = useCarrinho()

  return (
    <>
      <AppBar position="sticky" color="default" component="header">
        <Toolbar component="nav" aria-label="Navegação principal" sx={{ gap: 1, flexWrap: 'wrap' }}>
          <Typography component={RouterLink} to="/" variant="h6"
            sx={{ flexGrow: 1, color: 'primary.main', textDecoration: 'none', fontWeight: 800 }}>
            RINGSIDE
          </Typography>
          {ehAdmin && <Button component={RouterLink} to="/admin">Admin</Button>}
          {logado
            ? <Button onClick={sair}>Sair</Button>
            : <Button component={RouterLink} to="/login">Entrar</Button>}
          <IconButton component={RouterLink} to="/carrinho" aria-label={`Carrinho com ${quantidadeTotal} itens`}>
            <Badge badgeContent={quantidadeTotal} color="primary"><ShoppingCartOutlined /></Badge>
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="main">
        <Container sx={{ py: 3 }}>
          <Outlet />
        </Container>
      </Box>
    </>
  )
}
