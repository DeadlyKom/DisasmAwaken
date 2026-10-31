"""Два исходных CP866-потока описаний, разделители LF и абзацы CR сохраняются побайтово."""
from MarketScriptTable import parse
TABLES=(('PreviewShipText','Source/D3D/Data/ShipDescriptions.asm',0x3581,0x3BD8,('Dominion','Sofist','Memfis','Firs','Orsan','Baros','Karen')),
        ('PreviewSkimText','Source/D3D/Data/SkimmerDescriptions.asm',0x3BD8,0x3E6A,('Fervest','Kridon','Protos','Algol')))


def render(raw,table):
 module,path,start,end,names=table;blob=raw[start:end];starts=[i for i,v in enumerate(blob) if v==10];assert len(starts)==len(names)+(module=='PreviewSkimText') and starts[0]==0
 lines=['                module '+module,'                ; Документация [описания моделей](../../../Docs/PreviewDescriptions.md)','                ; исходная кодировка CP866, LF разделяет записи, CR разделяет строки и абзацы','                assert $ == #'+format(0xC000+start,'04X')];symbols={}
 for j,name in enumerate(names):
  offset=starts[j];stop=starts[j+1] if j+1<len(starts) else len(blob);record=blob[offset:stop];symbols[module+'.'+name]=0xC000+start+offset
  lines+=['                ; -----------------------------------------','                ; исходная запись '+str(j)+', '+record[1:].split(b'\r',1)[0].decode('cp866')]
  for paragraph in record[1:].decode('cp866').split('\r'):
   if paragraph:lines.append('                ; '+paragraph)
  for p in range(0,len(record),16):lines.append(((name+':').ljust(16) if p==0 else ' '*16)+'DB '+', '.join('#'+format(v,'02X') for v in record[p:p+16]))
 if len(starts)>len(names):
  assert starts[-1]==len(blob)-1;symbols[module+'.End']=0xC000+end-1;lines+=['                ; исходный конечный LF последнего описания','End:            DB #0A']
 lines+=['                endmodule'];text='\n'.join(lines)+'\n';actual,found=parse(text,0xC000+start);assert actual==blob and found==symbols
 return text,symbols
