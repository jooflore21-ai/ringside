import { createContext, useContext, useMemo, useState } from 'react'

const CarrinhoContext = createContext(null)

// Decisão de projeto: o carrinho vive só no front-end (estado local).
// O total aqui é apenas uma prévia; o servidor recalcula preço, total e estoque
// ao fechar o pedido, porque valor vindo do front nunca é confiável.
export function CarrinhoProvider({ children }) {
  const [itens, setItens] = useState([]) // [{ produto, quantidade }]

  const valor = useMemo(() => ({
    itens,
    quantidadeTotal: itens.reduce((soma, i) => soma + i.quantidade, 0),
    totalPrevia: itens.reduce((soma, i) => soma + Number(i.produto.preco) * i.quantidade, 0),
    adicionar(produto, quantidade = 1) {
      setItens((atuais) => {
        const existente = atuais.find((i) => i.produto.id === produto.id)
        const nova = Math.min((existente?.quantidade ?? 0) + quantidade, produto.estoque)
        if (existente) return atuais.map((i) => (i.produto.id === produto.id ? { ...i, quantidade: nova } : i))
        return [...atuais, { produto, quantidade: nova }]
      })
    },
    alterar(produtoId, quantidade) {
      setItens((atuais) => atuais.map((i) =>
        i.produto.id === produtoId ? { ...i, quantidade: Math.max(1, Math.min(quantidade, i.produto.estoque)) } : i))
    },
    remover(produtoId) {
      setItens((atuais) => atuais.filter((i) => i.produto.id !== produtoId))
    },
    limpar() {
      setItens([])
    },
  }), [itens])

  return <CarrinhoContext.Provider value={valor}>{children}</CarrinhoContext.Provider>
}

export const useCarrinho = () => useContext(CarrinhoContext)
