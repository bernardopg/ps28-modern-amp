# Referência mecânica fixa — placa original PS28

## Decisão do proprietário / D-014
Reutilizar o sistema de dissipação e os mesmos mounting points originais.
Gabinete, plate, carcaça traseira, suportes e fixação OEM passam a ser interfaces
fixas. A placa nova deve se adaptar a eles, não o contrário. Não criar furos no plate,
reposicionar suportes, cortar carcaça ou alterar vedação/isolação para caber o draft.

O retângulo 145×95 mm do core B é apenas organização provisória de componentes;
**não é reprodução do contorno ou furação da placa original**. J6 também não é
mounting point OEM: é uma feature GND interna do draft, a reavaliar conforme o conjunto.

## Fontes conferidas
Manual `reference/infinity/ps28-service-manual.pdf`, Rev1 3/2007.
Numeração abaixo é impressa; a página no PDF é uma unidade maior.
- p.8: vista explodida do conjunto gabinete/amplificador e fixação externa.
- p.15: dissipador de alumínio 323-AL-00020-0LAE, **65×32×31 mm**;
  suporte 362-FE-00041-0LAE, **11,75×8,5×12,5H mm**; isoladores TO-3P dos Q107/Q108.
- p.16: plate 302-AL-00406-1BDE, **300×200×2,5T mm**;
  carcaça 306-ABS-00177-0BAE, **198×298×102 mm**;
  dissipador preto 323-AL-00106-0BBE, **117,5×71,5×25 mm**;
  dois suportes L 362-FE-00013-0LAE, **89×9×1,6T mm**.
- p.17: desenho de componentes da main PCB, identificação **104-a05064a00-e**,
  e preamp; localização relativa de Q107/Q108, C121/C122 e interfaces.
- p.18: desenho do cobre. Conferir orientação/espelhamento antes de registrar pontos.

Correção da revisão anterior: o manual **não informa somente dimensões externas do
 gabinete**; sua BOM contém as dimensões acima. Elas são cotas nominais documentadas,
mas não dimensões da área interna livre nem mapa dimensionado de furos da PCB.
Não confundir tamanho da carcaça ABS com volume útil, nem contar todos os pads grandes
como furos de montagem: separar pads elétricos, apoios, parafusos e contatos de massa.

## Aplicação ao desenvolvimento
1. Usar main PCB e montagem OEM como datum mecânico. Registrar contorno, recortes,
   pontos de apoio e referência térmica em relação ao mesmo datum, preservando orientação.
2. Calibrar os desenhos com geometria documentada de componentes/interfaces, com
   checagem independente da escala. Não assumir que imprimir a página PDF em100%
   produz PCB1:1. Sem escala consistente, coordenadas gráficas não viram cotas finais.
3. Fazer o placement novo dentro do envelope original, mantendo interfaces e pontos
   de montagem. Se preciso, mudar posição de U1, contorno ou componentes do core B.
4. Reutilizar dissipadores, suportes e caminho mecânico de fixação. O TPA3255 DDV
   exige contato no PowerPAD SUPERIOR: os isoladores/clamps dos antigos TO-3P não
   são automaticamente uma interface equivalente. Projetar contato/pressão compatíveis
   sem levar carga aos leads; dissipador ligado a GND, nunca SPK±.
5. Validar sobreposição/gabarito na placa/suportes originais antes de fabricar.
   Isso é conferência do projeto referenciado no OEM, não um novo levantamento de todo
   o gabinete exigido para começar a trabalhar. Solicitar somente cotas locais que a
   reconstrução documental não consiga determinar com segurança.

## Evidência e limites
Dimensões/BOM transcritas em `ps28-original-integration.json`.
Páginas renderizadas em `build/mechanical-reference/pcb-18.png` e `pcb-19.png`;
fonte canônica é o PDF, não a resolução/escala dessas imagens.
A documentação não declara escala1:1 nem entrecentros de montagem cotados nesses
 desenhos. Fit e capacidade térmica ainda não aprovados; não inventar coordenadas para
concluir a furação. O orçamento térmico do core B permanece hipótese, não rating dos
 dissipadores OEM. Arquivo SCAD atual representa componentes, não conjunto OEM completo.
