"""Исходные ценовые строки и заголовок D3D, все управляющие байты сохраняются."""
from MarketScriptTable import parse
PATH='Source/D3D/Data/PreviewPrices.asm'
START=0xE40
END=0xEFA
RECORDS=(('Dominion','Доминион'),('Sofist','Софист'),('Memfis','Мемфис'),('Firs','Фирс'),('Orsan','Орсан'),('Baros','Барос'),('Karen','Карэн'),('Fervest','Фервест'),('Kridan','Кридан'),('Protos','Протос'),('Algol','Алгол'),('Heading','Модель'))


def render(raw):
 assert raw[0xECE:0xEFA].count(255)==31
 starts=[]
 for name,russian in RECORDS:
  position=raw.index(russian.encode('cp866'),START,END)-(name!='Heading');starts.append((position,name,russian))
 assert starts[0][0]==START and starts[-1][0]==0xECE and all(a[0]<b[0] for a,b in zip(starts,starts[1:]))
 lines=['                module PreviewPrices','                ; Документация [ценовые списки и временные разделители](../../../Docs/PreviewPrices.md)','                ; исходная кодировка CP866, код 02 задаёт колонку цены, CR и LF сохраняются','                assert $ == #CE40'];symbols={}
 for j,(start,name,russian) in enumerate(starts):
  end=starts[j+1][0] if j+1<len(starts) else END;blob=raw[start:end];symbols['PreviewPrices.'+name]=0xC000+start;lines+=['                ; -----------------------------------------','                ; '+russian+', исходные байты ценового потока']
  if name=='Karen':lines+=['                ; начальный LF отделяет Карэна от обычного рыночного списка, для собственного индекса 6 меняется на CR']
  if name=='Kridan':lines+=['                ; исходное имя Кридан сохранено, в описательном потоке исходник использует Кридон']
  if name=='Heading':lines+=['                ; 31 исходный байт FF после CR сохранены, они не заменяются пробелами ASCII']
  for i in range(0,len(blob),16):lines.append(((name+':').ljust(16) if i==0 else ' '*16)+'DB '+', '.join('#'+format(v,'02X') for v in blob[i:i+16]))
 lines+=['                endmodule'];text='\n'.join(lines)+'\n';actual,labels=parse(text,0xC000+START);assert actual==raw[START:END] and labels==symbols
 return text,symbols
