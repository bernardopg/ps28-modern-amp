# Skill — TPA3255 Reference Design Guardrails

## Missão

Impedir que o agente altere o núcleo TPA3255 sem base documental.

## Regras

1. Tratar datasheet TPA3255 e TPA3255EVM como golden reference.
2. Antes de alterar bootstrap, desacoplamento, mode pins, RESET, OC_ADJ, FREQ_ADJ, VDD/AVDD/DVDD/GVDD ou filtro LC:
   - identificar a referência oficial;
   - explicar a alteração;
   - listar efeito esperado;
   - listar validação necessária.
3. Nunca aterrar SPK+/SPK- em PBTL.
4. Nunca mover capacitores de desacoplamento para longe do CI por conveniência estética.
5. Marcar qualquer componente sem fonte confirmada como `TBD`.
6. Não liberar manufacturing output.

## Saída esperada

- componente/net afetado;
- referência oficial;
- risco;
- alteração proposta;
- teste necessário.
