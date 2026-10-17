# Simulação — cobertura, resultados e limites

## Estado verificado — 2026-10-16

A [CI do commit 4346009](https://github.com/bernardopg/ps28-modern-amp/actions/runs/38930461712)
terminou com **os dois jobs aprovados**: validações/modelos e macro oficial OPA1656.
Os três JSONs OPA1656/VMID/VMID protegido reproduziram **exatamente os resultados
versionados anteriores**, com ngspice 47. É confirmação de reprodutibilidade,
**não um novo modelo elétrico nem simulação completa da placa roteada**.

O avanço recente é o [orçamento térmico calculado](../mechanical/thermal-block.md)
e o fit nominal em CAD. Não é SPICE/FEM, ensaio térmico ou modelo calibrado do
perfil OEM→ambiente. Nenhuma simulação garante 150 W contínuos.

[Registro consolidado da CI](../tests/reports/simulation-ci-2026-10-16.json).
Logs/artefatos baixados ficam em `build/main-consolidation/ci/`, fora do Git;
modelos TI não são redistribuídos.

## O que foi efetivamente reexecutado na CI

- **LR4 ideal e LC diferencial:** regressão de ganho/resposta com fontes ideais;
  não simula o estágio de comutação do TPA3255.
- **LR4 com R/C explícitos:** 151 pontos AC, 16.384 corners e 2.048 amostras com
  seed fixa. Modelo comportamental limitado, não NE5532 real.
  Estudo e parâmetros.
- **OPA1656 oficial TI:** nove combinações de 10,8/12/13,2 V e 0/27/70 °C,
  AC e transiente. No testbench de referência, saída diferencial ≈1,99237 Vrms;
  desvio AC máximo ≈0,0003845 dB frente ao ideal. Avisos de gmin/source stepping
  estão registrados nos JSONs: resultado convergido não significa ausência de avisos.
  [Relatório](../tests/reports/opa1656-model-study.json).
- **VMID de referência:** 32 casos de return-ratio; margem de fase mínima
  **60,67°** sob o modelo/envelope declarado. O hard power-down do circuito
  passivo antigo continua inseguro — contraprova intencional, não uma aprovação.
  Estudo.
- **VMID protegido:** 30 casos de perda de alimentação e nove casos do testbench
  LR4 passam dentro do envelope declarado; não qualificam extremos de produção
  ou hardware. [Hipóteses e proteção](vmid-protection.md).
- **Power-order D-019:** 288 hipóteses, **196 violações intencionais preservadas**,
  incluindo exemplo de −2,75 V. RC e redes acopladas são conferidos contra
  equações/integração independentes. Sucesso significa detectar o perigo e
  preservar contraprovas; não que os 288 cenários sejam seguros para a PCB.
  [Contrato e limites](input-power-order-study.md).

## Estudos adicionais já existentes

Esses relatórios não foram transformados em novos ensaios por este push:

- **Fonte CT D-021:** 54 casos ngspice; PVDD máximo calculado **49,838 V**.
  Resistência/regulação do primário omitidas, diodo genérico e indutância de fuga
  varrida. Inrush/sag não são medidas. [Fonte e limites](power-d021.md).
- **Interface D-024/D-024a:** isolamento/mute e falha simples sob parâmetros
  declarados; [1350 + 216 casos](iso-d019.md), não qualificação de bancada.
- **Sequenciador:** verificação lógica da netlist e testes de mutação;
  não transiente SPICE completo. [D-020/D-023](seq-d020.md).
- **Térmica:** modelo de resistências concentradas, junção→perfil
  **2,249–3,975 °C/W** conforme TIM; sem R perfil→ambiente medida, espalhamento
  calibrado, vazios de interface ou FEM. [Relatório](../tests/reports/thermal-fit-review.json).

## Relação com a placa atual — importante

D-032 reaproveita o preamp/limiter OEM. Os testbenches LR4/front-end novo são
**referências históricas**, não extrações automáticas do preamp OEM, nem prova
de que a cadeia final completa foi simulada. A candidata contém interface,
proteção e sequenciamento; propriedades "não implementado/qualificado" dos estudos
antigos descrevem seus modelos/contratos, não a ausência desses blocos no CAD atual.

Ainda não há modelo completo extraído da PCB com parasitas de potência,
comutação/EMI do TPA3255, saturação real do LC, magnetismo/regulação medida de T1,
preamp OEM integral, acústica da caixa ou dissipador OEM→ambiente calibrado.
Não chamar repetição da CI de avanço nessa cobertura. O fechamento restante
segue revisão global/G1/G2, BOM/fit e BENCH-002, não uma alegação de simulação total.

## Reproduzir

```sh
make simulate                   # ideal, R/C, LC e contraprovas power-order
make simulate-opa               # exige macro TI local previamente auditado
python3 scripts/simulate_opa1656.py --fetch-model  # baixa e confere hash/diretivas
make simulate-vmid
make simulate-vmid-protected
make simulate-power
make thermal-fit                # cálculo/CAD, não SPICE ou FEM
```

Conferir versão de ngspice, hashes, premissas e cobertura antes de comparar
resultados. Fontes/envelopes em `simulation/` e relatórios em `tests/reports/`.
**Simulação não substitui G1/G2/G3, montagem real nem limites de bancada aprovados.**
