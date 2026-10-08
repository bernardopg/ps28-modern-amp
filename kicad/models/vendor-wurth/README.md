# CAD Würth — escopo e atribuição

Copyright Würth Elektronik eiSos GmbH & Co. KG. Arquivos STEP inalterados dos
pacotes oficiais KiCad rev26c, CC BY-SA 4.0:
https://creativecommons.org/licenses/by-sa/4.0/ . Avisos originais completos em
LICENSE.txt. A exceção para designs não elimina share-alike desta coleção CAD.
Não se aplica aos outros arquivos/ao projeto inteiro nem aos STEP diretos rev1.

- `CP_Wurth_WCAP-ATG5-P5D10L16.step`: WCAP-ATG5 D10/H16/P5 nominal,
  compatível mecanicamente com candidato 860020575014.
  Origem: https://www.we-online.com/components/products/download/KiCad_WCAP-ATG5%20%28rev26c%29.zip
  Membro: `3dmodels/Capacitor_THT_Wurth.3dshapes/CP_Wurth_WCAP-ATG5-P5D10L16.step`.
  SHA256 `11f68e0547f6812b472a84f3d5affd6a70778d47113482db6f6786ac86b0a0c6`.
- `L_Wurth_WE-HCF-2013.step`: case WE-HCF2013, candidato 7443631000.
  Origem: https://www.we-online.com/components/products/download/KiCad_WE-HCF%20%28rev26c%29.zip
  Membro: `3dmodels/Inductor_SMD_Wurth.3dshapes/L_Wurth_WE-HCF-2013.step`.
  SHA256 `f8b342ac40cd4caa08067c027411c74c2abb560f562cbca932eca4cabaa6e739`.

Acesso: 2026-10-08. Importação não troca pads/courtyards auditados. C1/C201/C202
usam transformação original; HCF usa rotação Z90° para corresponder à orientação
local, mantendo L2 180° no board. Tab HCF continua sem número/net.
Inspeção visual não é audit dimensional/tolerância/fit térmico; CAD simplificado
nominal não garante altura/corrente/folga. Não há aprovação de produção.
