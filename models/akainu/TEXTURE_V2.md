# Antebraço com textura extraída de lava e mud

Atualização de 28 de novembro de 2026. Foram utilizados os STL fornecidos pelo proprietário em `models/akainu/` para gerar uma nova casca com relevo de placas e fissuras.

## Método e fontes

- `Cracked_Lava_base_0.stl` fornece o relevo local de rocha. O 3MF correspondente identifica o trabalho como Cracked Lava Base 32 mm, de Matrix's Tabletop Emporium.
- `120x92 mud 1.stl` fornece a modulação de placas e fissuras maiores. O 3MF do conjunto identifica o trabalho como 120 x 92 mm Lava / Deep Cracked Mud Base Toppers, de dungeons and wyverns.
- Ambos os 3MF indicam Standard Digital File License. Os termos completos de redistribuição não foram confirmados. Os derivados e imagens de referência ficam locais, no diretório `v2/`, ignorado pelo Git. Confirmar licença antes de compartilhar esses arquivos ou usá-los comercialmente.

O gerador amostra a superfície superior de cada STL, recorta a região central para remover a borda da base e normaliza o relevo. Combina os dois campos e aplica o resultado radialmente à superfície externa do braço. O padrão é espelhado nas repetições para manter continuidade. Isso preserva placas e fissuras reais das fontes, com resolução limitada pela reamostragem. As bases planas e eventuais reentrâncias das malhas de origem não são transportadas.

## Arquivos locais gerados

- `v2/forearm_full_v2.stl` — referência completa com 230 mm de comprimento.
- `v2/forearm_wrist_v2.stl` e `v2/forearm_elbow_v2.stl` — duas metades de 115 mm, com contornos correspondentes na junção. A face de junção não possui encaixe mecânico.
- `v2/magma_sample_v2.stl` — amostra de aproximadamente 42,67 × 50 × 13,68 mm para primeiro teste.
- `v2/preview.png` — render da geometria, com cores ilustrativas.
- `v2/validation.json` — dimensões, volumes, hashes dos STL usados e resultados de validação.

Executar `generate_textured.py` com o Python do FreeCAD e NumPy, SciPy e Pillow disponíveis. Os arquivos de origem devem estar nos caminhos relativos acima.

## Ajuste e verificação

Foram mantidos os raios internos de 38 a 58 mm e o arco aberto de 140 graus. A parede varia de 2 a 8,2 mm, conforme o relevo; a espessura mínima é uma decisão provisória para teste. Não há canais perfurados, alojamentos eletrônicos ou fixações. A cor depende de material e pintura; o STL contém apenas geometria. A intensidade da luz através das fissuras requer teste de difusão.

As malhas foram verificadas quanto a fechamento, orientação das faces e triângulos degenerados, incluindo reabertura dos STL exportados em precisão de 32 bits. Foi verificada correspondência entre os contornos das duas metades. A inspeção de suportes, consumo e primeira camada no Bambu Studio, assim como os testes físicos, seguem pendentes.

Começar pela amostra e avaliar relevo em PLA antes de imprimir as metades. Manter o modelo completo como referência para conferir montagem e orientação. Os STL desta versão utilizam a mesma origem vertical entre metades; usar a função de apoiar na mesa no fatiador para imprimir cada uma separadamente.
