# Montagem e primeira energização

Procedimento da task [BENCH-002](../.tasks/items/BENCH-002.md). Não há ensaio de
bancada (D-037): a placa é montada no próprio gabinete e verificada com multímetro.
Só começar após G3 e com a placa recebida. Regras de [segurança](safety.md) valem sempre.

Material: multímetro, lâmpada-série incandescente 60–100 W (ou Variac) no primário,
pasta/TIM fino ≥3 W/(m·K), calços de precisão, chave Allen M3.

## 1. Montagem (dimensões)

1. Conferir apoios H5/H6 de mesma altura (3,1–3,5 mm, `mechanical/thermal-fit.json`).
2. Folga real entre pedestal do bloco e PowerPAD: **0,05–0,10 mm**, preenchida por TIM.
   O CI nunca é batente; quem limita a descida são os apoios.
3. Shim lateral sólido = vão medido − duas películas de TIM. Não forçar a PCB.
4. Parafusos: M3 lateral com engate útil na rosca OEM; M3×10 por baixo sem arruela larga.
5. Multímetro: continuidade J6 → bloco → perfil; nenhum lead/passivo tocando o bloco.
6. Ligar chicotes T1 (3 vias), preamp (7 vias) e fusível OEM 2,5 A no primário.
   **Woofer desconectado.**

## 2. Primeira energização (sem woofer)

1. Lâmpada-série no primário. Ao ligar, a lâmpada acende e apaga em segundos
   (carga dos 2×4700 µF). Se ficar acesa: desligar e procurar curto.
2. Medir nos TPs da tabela abaixo; limites em [requisitos](requirements.md) REQ-003/004.
   PVDD < 53,5 V sempre.
3. LEDs: PVDD, RAILS_OK e RUN acesos; FAULT e CLIP_OTW apagados.
4. Desligar, esperar o LED PVDD apagar, medir PVDD < 5 V antes de tocar na placa.

## 3. Woofer

1. Conectar o woofer, retirar a lâmpada-série, volume no mínimo.
2. Subir o volume aos poucos com música; ouvir estalos ao ligar/desligar e distorção.
3. Uso normal: CLIP_OTW não deve acender de forma persistente. Se acender, registrar
   condição e abrir decisão (D-037).

Parar por cheiro, fumaça, FAULT, aquecimento anormal ou tensão fora da faixa.
Desligar, aguardar descarga e diagnosticar; não insistir por tentativa.

## Pontos de medida e LEDs da placa (PCB-004)

Ponta preta do multímetro sempre em um TP **GND** (há um em cada ponta da placa).
Nunca usar SPK+/SPK− como referência: são saídas ativas.

| TP | Esperado (aparelho ligado, em repouso) |
|---|---|
| PVDD | 42–50 V DC |
| 12V | 12 V | 
| +15V / −15V | +15 V / −15 V (±1 V) |
| A12V | ~11 V | 
| VMID | metade de A12V |
| 3V3 | 3,3 V |
| GVDD | ~11 V (gerado pelo TPA) |
| RST, ROK | 3,3 V quando operando |
| FLT, OTW | alto = normal; baixo = falha / clip-térmico |
| DCOK | alto quando sem DC na saída |
| IN, D+, D−, INA, INB, CT | sinais: medir com osciloscópio, referência GND |

LEDs: **PVDD** aceso = bulk carregado (não mexer na placa enquanto aceso);
**RAILS_OK** trilhos na janela; **RUN** TPA liberado; **AUDIO** relé de entrada
fechado; **FAULT** e **CLIP_OTW** acesos = falha / clip ou aviso térmico.
Fan (J8): jumper JP701 em 1-2 sempre ligada; 2-3 liga com CLIP_OTW.
