# Bloco lógico D-018 — não outra PCB
Diagrama de13 componentes/27 pinos para revisar a fonte analógica/VMID.
A integração real do front-end vive em `../analog-protected/` (32/80,ERC0).
[Envelope, prova e gates pendentes](../../docs/vmid-protection.md).
J201=entrada AUX_RAW/GND; J202=ANALOG_12V/VMID/GND. Esses dois conectores são
interfaces do desenho auxiliar, não novos conectores/uma placa filha a fabricar.
Gerador atômico `scripts/create_vmid_protection.py`, sem sobrescrita.
Validação: `python3 scripts/check_vmid_protection.py`. Não fabricar/energizar.
