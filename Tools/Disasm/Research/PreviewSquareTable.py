"""Исходная свёрнутая таблица квадратов D3D, точные байты страницы C3."""
from MarketScriptTable import parse
PATH='Source/D3D/Data/FoldedSquare127.asm'
START=0x300
END=0x400


def render(source):
 raw=source[START:END];expected=bytes(min(i,255-i)**2//127 for i in range(256));assert raw==expected
 lines=['                module FoldedSquare127','                ; Документация [табличные приближения произведения](../../../Docs/PreviewLookupProducts.md)',
 '                ; T(i)=floor(min(i,255-i)^2/127), все исходные байты сохранены явно',
 '                assert $ == #C300']
 for start in range(0,256,16):
  lines.append('                ; индексы #'+format(start,'02X')+'..#'+format(start+15,'02X'))
  lines.append(('Values:'.ljust(16) if start==0 else ' '*16)+'DB '+', '.join('#'+format(v,'02X') for v in raw[start:start+16]))
 lines+=['                assert $ == #C400','                endmodule'];text='\n'.join(lines)+'\n';actual,labels=parse(text,0xC300);assert actual==raw and labels=={'FoldedSquare127.Values':0xC300}
 return text,labels
