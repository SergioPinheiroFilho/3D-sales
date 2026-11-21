# Roadmap de implementação

**Status em 2026-11-14.** Documentação consolidada e base Python local disponível. A pesquisa de mercado permanece pendente.

| Etapa | Objetivo | Entregável | Status |
|---|---|---|---|
| 0 | Validar mercado japonês | 10 oportunidades com fontes, custos e ranking | Parcial. [Triagem documental em três nichos](MARKET_RESEARCH_JP_2026-11-14.md) concluída. Demanda paga e custos pendentes |
| 1 | Preparar infraestrutura em paralelo à pesquisa | Git, Python, SQLite, configurações e controle de gastos | Parcial. Contratos, cálculo de margem e testes locais disponíveis |
| 2 | Implementar o MVP em duas entregas | Market Research JP local, depois integração com Coordenador e Financeiro | Proposta documentada. Implementação pendente |
| 3 | Rotinas semiautônomas | Logs, agendamento, relatórios, aprovação | Pendente |
| 4 | Produção física | Impressora, 3 protótipos e 3 SKUs testados | [Conceitos visuais disponíveis](PRODUCT_CONCEPTS.md). CAD, fabricação e testes pendentes |
| 5 | Primeiras vendas | Dados reais de 10–20 pedidos e revisão de margens | Pendente |
| 6 | Expansão | Marketing, Vendas, Produto e Dados; novos canais | Pendente |

## Próximas tarefas

Foi adicionada uma [pesquisa de cosplay e efeito de lava](COSPLAY_RESEARCH_2026-11-21.md). O antebraço iluminado é um candidato de protótipo para uso próprio. A escolha de priorizá-lo sobre os organizadores permanece aberta.
1. Revisar a migração local e integrar os arquivos ao histórico do `main` antes de publicar.
2. Implementar o fluxo local do Market Research JP, com entrada manual, persistência e ranking reproduzível.
3. Aprofundar o levantamento com 5 oportunidades de jogos de tabuleiro e 5 de action figures, comparáveis e custos. A triagem inicial de modelismo já está documentada.
4. Selecionar até três protótipos com base na pesquisa. Após aprovação e acesso a uma impressora, medir material, tempo de impressão, embalagem e frete.
5. Validar o fluxo do Mercado antes de integrar API, Coordenador e Financeiro. Configurar credenciais localmente e validar o controle de gastos antes de chamadas pagas.

## Regras de atualização
Ao concluir um marco, atualizar status, data, evidência e decisões no `DECISIONS.md`. Não marcar como concluído apenas por ter sido planejado.
