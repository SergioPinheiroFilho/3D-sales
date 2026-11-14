# 3D Sales Japan

Projeto de renda extra com impressão 3D FDM no Japão, apoiado por uma equipe semiautônoma de agentes OpenAI.

**Estado em 2026-11-14.** Planejamento e base Python local. A compra da impressora segue sem confirmação. Pesquisa, protótipos, vendas, integração com API e operação dos agentes seguem pendentes.

## Comece aqui

1. [Contexto e decisões](docs/PROJECT_CONTEXT.md)
2. [Roadmap](docs/ROADMAP.md)
3. [Pesquisa de mercado e nichos](docs/MARKET_RESEARCH.md)
4. [Economia e premissas](docs/FINANCIAL_MODEL.md)
5. [Arquitetura de agentes](docs/AGENT_ARCHITECTURE.md)
6. [Especificação do primeiro agente](agents/MARKET_RESEARCH_JP.md)
7. [Regras para assistentes](AGENTS.md)

## Estrutura

- `docs/`: decisões, hipóteses, estratégia e progresso.
- `agents/`: prompts e contratos dos agentes.
- `src/agents/`: implementação Python dos agentes.
- `src/services/`: banco de dados, fontes autorizadas e cálculos.
- `src/workflows/`: tarefas agendadas.
- `tests/`: testes automatizados.
- `data/`: dados locais (não versionar informações sensíveis).
- `config/`: configurações não secretas.

## Próxima etapa

Implementar o fluxo local do Market Research JP e usá-lo para avaliar 10 oportunidades com fontes e custos (5 de jogos de tabuleiro e 5 de action figures). Modelismo permanece prioritário para uma rodada posterior. A pesquisa embasa a escolha de até três protótipos. A integração com Coordenador e Financeiro vem após a validação do fluxo de pesquisa.

## Verificação local

Com Python 3.12 ou superior, execute `python -m unittest discover -v` a partir da raiz. A base atual usa a biblioteca padrão.
