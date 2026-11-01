"""Выделение трёх исполненных байтов DF6D из прежнего неразобранного диапазона."""
from pathlib import Path
import collections, contextlib, hashlib, io, json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 evidence=read('MusicRuntimeFlow');assert evidence['passed'] and evidence['unregistered_executed_pcs']==['DF6D']
 observed=next(i for i in evidence['instructions'] if i['address']==0xDF6D);assert set(observed['variants'].values())<={'LD HL,#0000','LD HL,#0002','LD HL,#FFFE'} or all(v.startswith('LD HL,#') for v in observed['variants'].values())
 pending={};sm=read('SourceMap');gap=next(e for e in sm if e['slot']==10 and e['offset']==0x46D);owner=next(e for e in sm if e['slot']==10 and e['offset']==0x447)
 oldpath=ROOT/gap['path'];raw=oldpath.read_bytes();assert gap['kind']=='unclassified' and gap['length']==3 and raw==bytes.fromhex('210000')
 assert owner['path']=='Source/Music/UnknownDF47.asm' and owner['length']==0x26
 original=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();owner['length']+=3;owner['sha256']=hashlib.sha256(original[0x447:0x470]).hexdigest();sm.remove(gap);pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encoded(sm)
 flow=read('ControlFlow');g=next(x for x in flow if x['name']=='Music');assert not any(i['address']==0xDF6D for i in g['instructions']);g['instructions'].append(dict(address=0xDF6D,operation='LD HL,#0000',hex='210000',slot=10,offset=0x46D));g['instructions'].sort(key=lambda x:(x['address'],x['slot'],x['offset']));g['instruction_count']+=1;g['code_bytes']+=3;g['classified_fraction']=g['code_bytes']/g['total_bytes'];pending[ROOT/'Tools/Disasm/Reports/ControlFlow.json']=encoded(flow)
 functions=read('Functions');f=next(x for x in functions if x['region']=='Music' and x['address']==0xDF47);assert f['end_offset']==0x46D;f['end_offset']=0x470;f.update(fallthrough_continuation=0xDF70,fragment_scope='modified_jr_then_pending_envelope_step');pending[ROOT/'Tools/Disasm/Reports/Functions.json']=encoded(functions)
 symbols=read('Symbols');symbols['Music.UnknownDF47.PendingStep']=0xDF6D;pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encoded(symbols)
 p=ROOT/f['path'];t=p.read_text('utf-8');needle='                endmodule\n                endmodule';assert t.count(needle)==1
 t=t.replace('; исходная запись 10, файловые смещения #0447..#046C','; исходная запись 10, файловые смещения #0447..#046F').replace(needle,'                ; Документация [наблюдавшийся вход](../../Docs/MusicEnvelopeStaging.md)\n                ; чтение отложенного шага после замены JR по DF6B на LD B,n\nPendingStep:    LD HL, #0000\n                ; JP @Music.UnknownDF70.Entry, продолжение в UnknownDF70.asm\n'+needle);pending[p]=t.encode('utf-8')
 p=ROOT/'Source/Files/10_MUZ1.inc';t=p.read_text('utf-8');needle='                assert $ == #046D\n                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/10_MUZ1/Unclassified012.bin"';assert t.count(needle)==1;t=t.replace(needle,'')
 for name,index in (('UnknownDF47',0),('UnknownDF70',1),('AdvancePatternA',2),('RenderChannelA',3)):
  needle='                include "../Music/'+name+'.asm"';assert t.count(needle)==1
  # Обновление номера только при уже существующем продолжении этой физической цепочки.
  line=next(l for l in t.splitlines() if l.startswith(needle))
  if ';' in line or name in ('UnknownDF47','UnknownDF70'):t=t.replace(line,needle.ljust(80)+'; ('+str(index)+') жёсткий порядок, последовательное исполнение')
 pending[p]=t.encode('utf-8')
 inventory=read('Inventory');inventory['instructions']+=1;inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in sm if e['kind']==k) for k in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in sm));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 candidate=ROOT/'Tools/Disasm/Research/Candidates/MusicEnvelopeStep';history=ROOT/'Tools/Disasm/Research/History/BeforeMusicEnvelopeStep';assert not candidate.exists() and not history.exists()
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);old=p.read_bytes();plan.append((p,old,data));c=candidate/rel;c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
 for p,old,data in plan:assert p.read_bytes()==old
 for p,old,data in plan:
  h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(old)
 h=history/oldpath.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(raw)
 for p,old,data in plan:p.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.resolve().is_relative_to((ROOT/'Source/Resources/10_MUZ1').resolve()) and oldpath.read_bytes()==raw==h.read_bytes();oldpath.unlink()
 result=dict(passed=True,new_instructions=1,new_code_bytes=3,address=0xDF6D,original_bytes='210000',physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MusicEnvelopeStepDiscovery.json').write_bytes(encoded(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
