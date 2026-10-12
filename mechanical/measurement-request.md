# Medidas que faltam — dissipador/TPA3255 e woofer (2026-10-12, D-030)

Já medido e registrado (não repetir): contorno da placa 154×81 mm, furos M3 de fixação,
perfil U 65×33×30 mm, posição do perfil, furos dos TO-3P (12,7 mm das pontas, 6,35 mm
da PCB), altura livre acima dos capacitores, T1 34,35 VAC/metade, Re do woofer 4,4 Ω,
etiqueta 20PR10DAG-FW06-E, cone livre. Ver `oem-heatsink-measurements.md`,
`oem-harness-sealing.md` e `owner-clearance-20261012.json`.

## Segurança antes de começar

Aparelho **desligado da tomada há pelo menos 10 min**. Antes de tocar na placa, medir
em DC (escala 200 V) os terminais de C121 e C122: só continuar abaixo de 2 V. Se houver
tensão, descarregar com resistor de 100 Ω a 1 kΩ / 5 W segurado por alicate isolado,
nunca com chave de fenda em curto.

## A. Dissipador / contato do TPA3255 (régua ou paquímetro)

A1. Furos dos TO-3P na perna do perfil U: **roscados (M3) ou passantes com porca?**
    Remover um parafuso e anotar comprimento e diâmetro (BOM lista M3×14).
A2. Entre o TO-3P e o perfil há **isolante** (mica/silicone)? Cor e espessura aproximada.
A3. Com os TO-3P removidos: a face da perna é **plana e lisa** onde eles encostavam?
    Anotar rebarba, pintura/anodização ou pasta seca.
A4. Continuidade (multímetro em Ω/beep) entre o **perfil U e o backplate**, e entre o
    perfil e o **GND da placa original** (terminal negativo de C121). Anotar Ω.
A5. Distância da **face da perna até a borda dos componentes vizinhos** na placa original
    (só se houver algo a menos de 5 mm da perna). Senão, escrever "livre".

## B. Woofer (multímetro, sem amplificador ligado)

B1. Desconectar os dois fios do woofer da placa. Anotar a **cor de cada fio** e qual
    terminal do woofer tem marca (+, ponto vermelho ou terminal maior).
B2. Polaridade com o multímetro: escala **DC 200 mV**, ponta vermelha no terminal
    marcado +, preta no outro. **Empurrar o cone devagar para dentro** com a palma
    da mão e observar o primeiro número: positivo ou negativo? (Positivo: a marcação
    está correta. Negativo: o + real é o outro terminal.) Não usar pilha.
B3. Confirmar Re de novo só se os fios forem trocados: escala 200 Ω, descontar a
    resistência das pontas encostadas (já feito: 4,4 Ω).

## C. Conector de T1 (multímetro em Ω, aparelho fora da tomada)

C1. Com o conector de 3 vias do T1 desligado da placa, medir resistência entre os
    pinos: vermelho1–preto, preto–vermelho2 e vermelho1–vermelho2. Esperado:
    as duas primeiras parecidas e a terceira ≈ soma delas. Anotar os três valores.
C2. Anotar a ordem física dos fios no conector (de um lado para o outro).

Enviar as respostas como texto (A1…C2). Fotos ajudam em A2/A3, mas são opcionais.
