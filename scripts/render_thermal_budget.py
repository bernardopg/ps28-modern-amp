#!/usr/bin/env python3
"""Plot calculated scenarios and label the Blender study views, never measurements."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/TTF/DejaVuSans.ttf'
if not Path(FONT).is_file():FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(n):return ImageFont.truetype(FONT,n)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot-only',action='store_true',help='Do not annotate already-stamped Blender views')
    args=parser.parse_args()
    r=json.loads((ROOT/'tests/reports/thermal-fit-review.json').read_text())
    w,h=1400,1080;im=Image.new('RGB',(w,h),'#f4f6f8');d=ImageDraw.Draw(im)
    d.text((55,25),'Orçamento térmico — cenários calculados, NÃO ensaio',font=font(30),fill='#172b40')
    d.text((55,75),'Ta = 40 °C; perdas atribuídas a U1; caminho OEM ao ambiente NÃO medido',font=font(22),fill='#293b4b')
    d.text((30,125),'Tj [°C]',font=font(19),fill='#334455')
    x0,y0,x1,y1=110,160,1320,800
    xy=lambda p,t:(x0+(p-5)/15*(x1-x0),y1-(t-40)/200*(y1-y0))
    for temp in range(40,241,20):
        y=xy(5,temp)[1];d.line((x0,y,x1,y),fill='#d4dce3');d.text((30,y-12),str(temp),font=font(19),fill='#334455')
    for power in range(5,21,5):
        x=xy(power,40)[0];d.line((x,y0,x,y1),fill='#d4dce3');d.text((x-12,y1+12),str(power),font=font(20),fill='#334455')
    for temp,label,color in [(110,'110 °C — alvo de projeto assumido','#b77b00'),(125,'125 °C — máximo recomendado TI','#b12839')]:
        y=xy(5,temp)[1];d.line((x0,y,x1,y),fill=color,width=3);d.text((x0+15,y-28),label,font=font(19),fill=color)
    worst=r['thermal']['r_junction_to_profile_range_K_W'][1]
    for resistance,color in [(1.5,'#087f8c'),(3,'#4058b0'),(5,'#9d3c8f')]:
        points=[xy(p,40+p*(resistance+worst)) for p in [5,10,15,20]]
        d.line(points,fill=color,width=5)
        for x,y in points:d.ellipse((x-5,y-5,x+5,y+5),fill=color)
        d.text((130,900+int((resistance==3)*32+(resistance==5)*64)),f'R caminho OEM = {resistance:g} °C/W (hipótese)',font=font(21),fill=color)
    d.text((x0+330,y1+45),'Potência dissipada em U1 [W] — não é potência no woofer',font=font(21),fill='#172b40')
    d.text((45,h-30),'R local pior caso ≈ 3,97 °C/W. Projeto não liberado; não extrapolar rating contínuo.',font=font(19),fill='#172b40')
    im.save(ROOT/'docs/images/thermal-budget.png')
    if args.plot_only:return
    titles={'thermal-block.png':'Bloco revisto — rasgos em z=23,65 mm; roscas não modeladas',
            'thermal-block-bottom.png':'Pedestal 6×3 mm; batentes/calços obrigatórios, não o encapsulamento',
            'thermal-fit-assembly.png':'Montagem nominal — perfil OEM, calço sólido e plaquetas de apoio',
            'thermal-fit-section.png':'Seção central — envelopes de altura, não corpos MPN qualificados',
            'thermal-fit-contact.png':'Contato nominal: TIM 0,05 mm; selecionar batentes no conjunto REAL'}
    for name,title in titles.items():
        path=ROOT/'docs/images'/name;original=Image.open(path).convert('RGB')
        # Blender re-generates clean views before this command; avoid stacking labels.
        if original.height!=1000:raise ValueError('Regenerate clean Blender views before annotating')
        canvas=Image.new('RGB',(original.width,original.height+100),'#172b40');canvas.paste(original,(0,68));draw=ImageDraw.Draw(canvas)
        draw.text((20,8),'ESTUDO CAD — NÃO FABRICAR — SEM ENSAIO TÉRMICO',font=font(24),fill='white')
        draw.text((20,38),title,font=font(19),fill='#d5e1ee')
        draw.text((20,original.height+75),'Cotas em mechanical/thermal-fit.json; interferências nominais não comprovam fit físico.',font=font(17),fill='white')
        canvas.save(path)

if __name__=='__main__':main()
