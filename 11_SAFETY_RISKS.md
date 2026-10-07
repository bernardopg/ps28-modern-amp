# Segurança e riscos

## Decisão principal de segurança

A Rev. A usa **fonte externa isolada de 36 VDC**. Não integrar rede 127/220 VAC ao primeiro projeto.

Isso remove da PCB customizada a maior parte dos riscos de:

- choque letal;
- creepage/clearance de rede;
- certificação de fonte;
- fusível/EMI de primário;
- isolamento reforçado;
- transformador SMPS.

## Mesmo em 36 V

A potência disponível é alta. Um curto pode:

- vaporizar trilhas;
- incendiar componentes;
- destruir o woofer;
- danificar instrumento de medição.

Use fusível e current limit durante desenvolvimento.

## Osciloscópio e saída BTL/PBTL

SPK+ e SPK- são saídas ativas. Não prender o ground clip de um osciloscópio aterrado diretamente a um terminal do speaker sem entender o isolamento do instrumento. Use sonda diferencial ou método seguro apropriado.

## Capacitores

Capacitores bulk podem permanecer carregados. Confirmar tensão antes de manusear/retrabalhar.

## IA

Nenhuma alteração feita por agente de IA deve ser tratada como validada apenas por compilar ou passar DRC.

## Fabricação

Antes de enviar:

- revisão humana do schematic;
- revisão humana do layout;
- comparação com TPA3255EVM;
- checagem de footprints e polaridades;
- plano de teste pronto.
