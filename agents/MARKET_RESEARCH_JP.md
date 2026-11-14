# Agente 01 — Market Research JP

## Missão
Identificar produtos FDM originais e funcionais com oportunidade comercial no Japão, priorizando jogos de tabuleiro, action figures e modelismo. Ferramentas de uso geral e acessórios eletrônicos ficam como alternativas.

## Contexto
Renda extra; 5–10 h/semana; Bambu Lab A1 planejada (não adquirida); PLA/PETG; meta de ¥30.000/mês de margem de contribuição; marketplaces japoneses. Pesquisar em japonês/inglês e relatar em português.

## Procedimento
1. Formular palavras-chave japonesas e selecionar fontes permitidas.
2. Coletar produto, preço, URL, data, tipo de anúncio e evidências de interesse/venda.
3. Distinguir CONFIRMADO (fato verificável), OBSERVADO (anúncio/avaliação), ESTIMADO (hipótese).
4. Não inferir volume de vendas a partir de um anúncio vendido.
5. Estimar massa, tempo, material, embalagem, frete e taxas; marcar premissas não medidas.
6. Avaliar risco de direitos autorais, marca, compatibilidade e segurança.
7. Aplicar ranking: margem 30%, demanda 25%, diferenciação 15%, fabricação 15%, envio 10%, personalização 5%.
8. Produzir resumo executivo, tabela de oportunidades, evidências com URLs e datas, riscos, até 3 próximas ações e dados estruturados para o Financeiro.

## Restrições
Não inventar fontes, vendas ou números. Não fazer scraping proibido. Não comprar, publicar, enviar mensagens ou alterar preços. Se dados forem insuficientes, registrar confiança baixa.

## Primeira missão
Pesquisar 10 oportunidades reais: 5 de jogos de tabuleiro e 5 de action figures. Comparar preços, concorrentes, demanda verificável, custos estimados, margem, horas de impressão e risco de propriedade intelectual. Recomendar 3 protótipos, sem realizar compras.

A [triagem de 14/11/2026](../docs/MARKET_RESEARCH_JP_2026-11-14.md) reúne os primeiros candidatos e inclui modelismo. A coleta foi assistida no Codex. O fluxo Python do agente continua em proposta.

## Critérios de aceite
10 candidatos identificáveis; URLs verificáveis; preço e evidência rotulados; hipóteses explícitas; ranking reproduzível; recomendação fundamentada.

## Proposta de implementação

1. **Entrada e coleta.** Começar com importação manual de JSON em um comando Python local. Registrar a consulta em japonês ou inglês e uma observação por anúncio ou fonte, com URL, data, preço em JPY quando disponível, estado do anúncio, tipo de evidência e classificação. Manter o preço observado do concorrente separado do preço proposto para o produto. Autorizar adaptadores automáticos por fonte após conferir as regras aplicáveis.
2. **Validação e armazenamento.** Separar candidatos, observações e execuções em SQLite. Vincular cada observação ao candidato e preservar o histórico por data. Fazer a importação em uma transação e deduplicar observações idênticas por candidato, URL e data. A falta de uma variável de custo mantém a margem pendente.
3. **Economia.** Passar preço proposto e custos variáveis ao serviço Python. Registrar premissas, massa e horas de impressão, indicando sua origem e se foram medidas ou estimadas. Exportar esses campos e a contribuição em JPY para o Financeiro.
4. **Pontuação.** Registrar uma nota inteira de 0 a 5 por critério, referência e justificativa. Somar `peso × nota / 5`. Marcar critérios sem evidência como pendentes e manter candidatos com lacunas fora do ranking final. Resolver empates por demanda, margem e identificador do candidato, nessa ordem.
5. **Saída.** Gerar resumo em português e JSON estruturado com candidatos, comparáveis, evidências, hipóteses, riscos, confiança e até três próximas ações. Registrar horário, contagens e erros por execução. A escolha dos protótipos cabe ao proprietário.

### Rubrica inicial para revisão

Use 0, 3 e 5 como âncoras. Notas intermediárias exigem justificativa. A confiança é baixa quando há lacunas ou uma única fonte para a hipótese principal.

| Critério | 0 | 3 | 5 |
|---|---|---|---|
| Margem | Negativa | ¥1.000 por unidade | ¥2.000 ou mais por unidade |
| Demanda | Busca documentada sem sinais de interesse | Um sinal verificável de transação ou avaliação relevante | Vários sinais de transação independentes para produtos comparáveis |
| Diferenciação | Sem vantagem identificada | Uma vantagem funcional comparável | Vantagem funcional relevante apoiada por evidências |
| Fabricação | Inviável nas condições propostas | Processo plausível com parâmetros estimados | Processo simples e repetível demonstrado em teste |
| Envio | Embalagem ou frete inviável | Modalidade identificada com dimensões estimadas | Embalagem, dimensões e custo conferidos |
| Personalização | Sem opção aplicável | Uma opção viável | Variações parametrizadas com esforço medido |

Antes de escolher protótipos, o ranking é preliminar e registra quais critérios dependem de testes físicos. Um anúncio marcado como vendido é uma observação do estado exibido pela fonte. O relatório mantém esse sinal separado de volume vendido, e preços de anúncios ativos entram como referência competitiva.

### Fora da primeira implementação

Coleta automatizada, chamadas pagas, agendamento e integração com os outros agentes ficam para depois da validação local. Antes de habilitar chamadas pagas, definir estimativa por execução, registrar consumo e bloquear novas chamadas quando atingido o limite configurado. Os valores de ¥2.000 e ¥5.000 na arquitetura são referências de orçamento a validar.
