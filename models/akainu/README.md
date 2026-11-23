# Casca de magma — protótipo geométrico v1

Criado em 23 de novembro de 2026. Modelo inicial com volumes orgânicos sobre uma casca curva, baseado no conceito de antebraço de magma. O proprietário informou 230 mm de antebraço, diâmetro de 70 mm no punho e 110 mm na parte maior. Foram adicionados 3 mm radiais de folga como hipótese inicial para forro. A seção foi aproximada por círculos e precisa de teste de ajuste.

![Vista da geometria gerada](preview.png)

## Arquivos

- `lava_sketch_plate.FCStd` — placa reta de 150 × 150 × 2 mm e esboço nativo Sketcher traçado a partir das faixas laranja da imagem fornecida. Abrir no FreeCAD e dar duplo clique em `Lava - linhas centrais editaveis` para editar. A placa é um objeto Box com dimensões editáveis. A imagem retangular foi preservada na proporção original, com desenho de 140 mm de largura centralizado na placa. O esboço fica 0,05 mm acima da face superior para facilitar visualização.
- `lava_sketch_preview.png` — prévia dos eixos extraídos da imagem. O traçado automático simplifica curvas em segmentos e descarta pequenos fragmentos. As linhas são geometria normal, livres e sem restrições, para permitir edição. Não são linhas de construção azuis do Sketcher. Há ramificações abertas; fechar os contornos antes de extrudar áreas. Os pontos coincidentes visualmente podem exigir restrições de coincidência após edição.
- `trace_lava.py` — gerador do documento, executado com o Python do FreeCAD 1.0 e suas bibliotecas NumPy, SciPy e Pillow. Recebe o caminho da imagem como argumento. O documento foi salvo e reaberto para conferir a contagem de geometrias.

- `forearm_concept.stl` e `.obj` — referência completa de 230 mm de comprimento, arco de 140 graus, raio interno variando de 38 a 58 mm. Aberta nas laterais e extremidades, com parede fechada em toda a borda. O comprimento supera a mesa da A1 mini na orientação longitudinal.
- `forearm_wrist.stl` e `forearm_elbow.stl` — metades de 115 mm para a A1 mini, também disponíveis em OBJ. A divisão é plana, com bordas adjacentes. A união e as fixações precisam ser projetadas após teste das peças. Não há encaixe mecânico entre as metades nesta versão.
- `magma_sample.stl` e `.obj` — amostra de aproximadamente 40,11 × 50 × 14,09 mm para começar os testes.
- `generate.py` — gerador editável em Python com NumPy. Executar `python models/akainu/generate.py` a partir da raiz. Os parâmetros estão no final do script.
- `validation.json` — dimensões, volumes e verificações de fechamento da malha.

As malhas passaram na verificação de triângulos não degenerados, duas faces por aresta, orientação consistente e topologia fechada. A impressão física e a validação no fatiador permanecem pendentes.

## Como testar

Importar primeiro `magma_sample.stl` no Bambu Studio usando unidades em milímetros. Conferir dimensões, orientação, apoios, suportes e consumo na prévia de camadas. A superfície interna é curva, portanto pode exigir suportes conforme a orientação. Começar com PLA disponível para avaliar geometria; depois experimentar material translúcido para luz.

STL e OBJ contêm geometria sem pintura. O vermelho da prévia é ilustrativo. A malha possui relevos sólidos com vales entre os volumes; a espessura varia de 2 mm até cerca de 9 mm. A difusão de luz precisa de ajuste de espessura após teste. As crostas pretas podem ser estudadas por pintura ou peças adicionais.

O modelo ainda precisa de ajuste anatômico, bordas de contato suavizadas, fixações, alojamentos de LED e desenvolvimento da peça da mão. O relevo é uma aproximação procedural inicial do conceito. Confirmar a seção real do braço e o espaço para forro e eletrônica com testes físicos antes de usar a casca como peça vestível.
