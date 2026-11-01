"""Выделение доказанного входа DB8C из хвоста глушения AY без изменения байтов."""
from pathlib import Path
import collections, contextlib, hashlib, io, json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
import MusicEnvelopeCommandFacts as facts


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('MusicEnvelopeCommandVerification')['passed'];candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicEnvelopeCommand';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicEnvelopeCommand';assert not candidate.exists() and not history.exists();pending={}
 functions=read('Functions');old=next(f for f in functions if f['region']=='Music' and f['address']==0xDB7C);assert old['end_offset']==0xA0;old['end_offset']=0x8C
 path='Source/Music/ReadEnvelopeSlide.asm';name,description=facts.FUNCTIONS[0xDB8C];f=dict(region='Music',name=name,address=0xDB8C,slot=10,offset=0x8C,end_offset=0xA0,path=path,description=description,semantic_status='described');functions.insert(functions.index(old)+1,f);pending[ROOT/'Tools/Disasm/Reports/Functions.json']=encoded(functions)
 flow=read('ControlFlow');g=next(x for x in flow if x['name']=='Music');g['roots']=sorted(set(g['roots'])|{0xDB8C});pending[ROOT/'Tools/Disasm/Reports/ControlFlow.json']=encoded(flow)
 lines=['                module Music','                module '+name,'                ; Документация [команда скольжения огибающей](../../Docs/MusicEnvelopeStaging.md)','                ; -----------------------------------------','                ; '+description,'                ; исходная запись 10, файловые смещения #008C..#009F']
 for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Music',0xDB8C]):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------']
 rows=[i for i in g['instructions'] if 0xDB8C<=i['address']<0xDBA0]
 for n,i in enumerate(rows):
  before,right=facts.COMMENTS.get(i['address'],([],None));assert right is None;lines+=['                ; '+v for v in before];lines.append(('Entry:'.ljust(16) if n==0 else ' '*16)+facts.name_operands('Music',0xDB8C,i['operation'].replace(',',', ')))
 lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
 p=ROOT/old['path'];t=p.read_text('utf-8');needle='                LD A, (DE)';start=t.index(needle);assert t[:start].rstrip().endswith('RET');t=t[:start]+'                endmodule\n                endmodule\n';t=t.replace('#007C..#009F','#007C..#008B');pending[p]=t.encode('utf-8')
 sm=read('SourceMap');entry=next(x for x in sm if x['slot']==10 and x['offset']==0x7C);assert entry['length']==0x24;raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();entry['length']=16;entry['sha256']=hashlib.sha256(raw[0x7C:0x8C]).hexdigest();sm.insert(sm.index(entry)+1,dict(slot=10,offset=0x8C,length=20,kind='code',path=path,origin=0xDB8C,sha256=hashlib.sha256(raw[0x8C:0xA0]).hexdigest()));pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encoded(sm)
 p=ROOT/'Source/Files/10_MUZ1.inc';t=p.read_text('utf-8');needle='                assert $ == #00A0';assert t.count(needle)==1;t=t.replace(needle,'                assert $ == #008C\n                disp #DB8C\n                include "../Music/ReadEnvelopeSlide.asm"\n                ent\n'+needle);pending[p]=t.encode('utf-8')
 symbols=read('Symbols');assert 'Music.ReadEnvelopeSlide.Entry' not in symbols;symbols['Music.ReadEnvelopeSlide.Entry']=0xDB8C;pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encoded(symbols)
 mod=read('ModifiedCode')
 for x in mod:
  if x['region']=='Music' and 0xDB8C<=x['writer']<0xDBA0:x['path']=path
 assert not any(x['region']=='Music' and x['writer']==0xDB97 for x in mod)
 mod.append(dict(region='Music',writer=0xDB97,target=0xDF6E,target_instruction=0xDF6D,size=2,target_operation='LD HL,#0000',path=path,target_region='Music',target_bank=3,target_slot=10,writer_bank=3));pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encoded(mod)
 inventory=read('Inventory');inventory['fragments']+=1;inventory['described']+=1;inventory['ranges_by_kind']=dict(collections.Counter(x['kind'] for x in sm));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 for filename,extra in (
  ('Knowledge.py',"\nfrom MusicEnvelopeCommandFacts import FUNCTIONS as MUSIC_ENVELOPE_COMMAND_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_ENVELOPE_COMMAND_FUNCTIONS)\n"),
  ('Contracts.py',"\nfrom MusicEnvelopeCommandFacts import CONTRACTS as MUSIC_ENVELOPE_COMMAND_CONTRACTS\nCONTRACTS.update(MUSIC_ENVELOPE_COMMAND_CONTRACTS)\n"),
  ('MusicNotes.py',"\nfrom MusicEnvelopeCommandFacts import COMMENTS as MUSIC_ENVELOPE_COMMAND_COMMENTS\nCOMMENTS.update(MUSIC_ENVELOPE_COMMAND_COMMENTS)\n"),
  ('SemanticNames.py',"\nfrom MusicEnvelopeCommandFacts import name_operands as music_envelope_command_name_operands\nDOCUMENTS['Music',0xDB8C]=('MusicEnvelopeStaging','команда скольжения огибающей')\n")):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from MusicEnvelopeCommandFacts import' not in t
  if filename=='SemanticNames.py':
   needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = music_envelope_command_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');assert '| Music | 27 | 15 |' in t;t=t.replace('| Music | 27 | 15 |','| Music | 28 | 16 |');t+='\n| #DB8C | [Music.ReadEnvelopeSlide](../Source/Music/ReadEnvelopeSlide.asm) | '+description+' |\n';pending[p]=t.encode('utf-8')
 p=ROOT/'Docs/FunctionDetails/Music.md';pending[p]=(p.read_text('utf-8')+'\n## ReadEnvelopeSlide\n\n[Music.ReadEnvelopeSlide](../../Source/Music/ReadEnvelopeSlide.asm) — '+description+'. [Алгоритм](../MusicEnvelopeStaging.md).\n').encode('utf-8')
 p=ROOT/'Docs/ModifiedCode.md';pending[p]=(p.read_text('utf-8')+'\n| Music | #DB97 | #DF6E | Music, банк 3, LD HL,nn по DF6D | [ReadEnvelopeSlide.asm](../Source/Music/ReadEnvelopeSlide.asm) |\n').encode('utf-8')
 plan=[]
 for p,data in pending.items():
  old=p.read_bytes() if p.exists() else None;plan.append((p,old,data));c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old if old is not None else not p.exists()
 for p,old,data in plan:
  if old is not None:h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 for p,old,data in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 result=dict(passed=True,new_semantic_entry=0xDB8C,physical_split_bytes=20,instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MusicEnvelopeCommandClassification.json').write_bytes(encoded(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
