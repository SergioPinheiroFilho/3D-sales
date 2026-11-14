# Arquitetura da equipe semiautônoma — opção B

## Visão
Proprietário aprova decisões → Coordenador distribui análises → agentes especializados → banco compartilhado → relatório semanal e fila de aprovação.

## Sete papéis
1. Coordenador: distribui tarefas, consolida relatórios e recomenda ações.
2. Mercado: oportunidades, concorrência, evidências e preços.
3. Produto: CAD, viabilidade, material, impressão, riscos.
4. Financeiro: custos, margem, caixa, cenários.
5. Marketing: títulos, descrições e palavras-chave em japonês.
6. Vendas: histórico de anúncios, pedidos, preços e reposição.
7. Dados: qualidade, dashboards, métricas e alertas.

## MVP
Implementar primeiro o Market Research JP e validar seu fluxo local. Em seguida, integrar Coordenador e Financeiro ao MVP.

## Base Python local

- `src/agents/contracts.py` define o protocolo tipado de execução e os tipos de classificação e referência de fonte.
- `src/services/finance.py` calcula contribuição unitária em ienes inteiros. O chamador informa todos os custos variáveis, inclusive comissão e perdas.
- `src/workflows/` receberá a entrada do operador e a orquestração. A proposta do primeiro fluxo está na [especificação do Market Research JP](../agents/MARKET_RESEARCH_JP.md).
- SQLite, adaptadores externos, fila de aprovação, execução agendada e controle de gastos permanecem planejados.

## Stack planejada
Python, OpenAI API/Agents SDK, SQLite, Google Sheets opcional, Streamlit opcional, Git/GitHub, agendamento local via Windows Task Scheduler/cron. Hospedagem só se necessário.

## Permissões
Automático: pesquisa em fontes autorizadas, análise, cálculos, rascunhos, relatórios.
Aprovação: publicação, alterações de preço, compras, envio de mensagens, alteração de registros financeiros confirmados.
Proibido: pagamentos autônomos, contorno de restrições, exposição de credenciais e execução de comandos não confiáveis de sites.

## Rotina proposta
Segunda: mercado. Terça: finanças. Quarta: marketing. Sexta: relatório. Fim de semana: revisão e CAD.

## Custos
Orçamento-alvo API/pesquisa ~¥2.000/mês; teto pretendido ¥5.000/mês, a validar por preços atuais e consumo. API é separada do ChatGPT Plus. Registrar tokens e gastos; implementar limite no código além de alertas.

## Estrutura de dados
Produtos, concorrentes, observações, vendas, custos, execuções, decisões e aprovações. Toda observação externa deve ter fonte, data e classificação: confirmada, observada ou estimada.
