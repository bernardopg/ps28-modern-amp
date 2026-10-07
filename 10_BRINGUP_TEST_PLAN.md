# Bring-up e Plano de Teste

> Nunca conectar o woofer na primeira energização.

## Equipamento mínimo

- fonte de bancada 0–40 V com current limit, idealmente ≥5 A;
- multímetro;
- osciloscópio com sondagem apropriada;
- gerador de sinais;
- carga resistiva de potência 4 Ω dimensionada para os ensaios;
- termopar ou câmera térmica desejável.

## Etapa 0 — placa sem energia

- inspeção óptica;
- continuidade GND;
- resistência PVDD→GND;
- verificar polaridade;
- inspeção de solda do PowerPAD se possível por processo/raio-X do fabricante;
- confirmar ausência de bridge.

## Etapa 1 — rails auxiliares sem power stage ativo

Se o projeto permitir isolar RESET:

1. aplicar tensão baixa inicialmente;
2. validar 12 V;
3. validar VMID;
4. validar 3.3 V se usado;
5. confirmar RESET em estado seguro.

## Etapa 2 — PVDD limitado

- iniciar com current limit baixo;
- aumentar PVDD gradualmente;
- observar consumo;
- checar FAULT/CLIP;
- checar aquecimento anormal.

## Etapa 3 — sinal analógico

Aplicar seno de baixa amplitude:

- RCA L;
- RCA R;
- RCA LFE.

Medir:

- soma L/R;
- saída do LPF;
- saída do buffer LFE;
- DIFF_A/DIFF_B.

## Etapa 4 — saída sem carga

Usar técnica de medição compatível com saída bridge/Class-D. **Não aterrar inadvertidamente uma ponta de osciloscópio em SPK+ ou SPK-** se o equipamento de medição não for isolado/diferencial.

## Etapa 5 — carga resistiva

Começar em baixa potência.

Medir:

- tensão RMS diferencial na carga;
- potência calculada;
- THD se houver instrumento;
- temperatura de TPA/indutores;
- clipping;
- comportamento de FAULT.

Progredir em etapas: 1 W → 10 W → 25 W → 50 W → 100 W → alvo, somente se térmica e forma de onda estiverem corretas.

## Etapa 6 — woofer

Somente depois de passar carga resistiva:

- iniciar em volume mínimo;
- seno 40–80 Hz baixo;
- depois música/LFE;
- checar ruído mecânico;
- validar excursão e temperatura.

## Critérios de parada imediata

- corrente inesperada;
- cheiro/aquecimento rápido;
- FAULT persistente;
- DC diferencial relevante na saída;
- ringing/oscilações anormais;
- indutor saturando;
- temperatura subindo sem estabilização.
