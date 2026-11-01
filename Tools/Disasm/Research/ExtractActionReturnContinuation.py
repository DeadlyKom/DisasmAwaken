"""Выделение ровно CALL ResumePointer по адресу, помещаемому исходным действием на стек."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('PackedWordAndActionReturnVerification')['passed'];candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionReturnContinuation';history=ROOT/'Tools/Disasm/Research/History/BeforeActionReturnContinuation';assert not candidate.exists() and not history.exists();pending={}
 source_map=read('SourceMap');entry=next(e for e in source_map if e['slot']==4 and e['offset']==0x21DC);oldpath=ROOT/entry['path'];raw=oldpath.read_bytes();assert entry['kind']=='unclassified' and entry['length']==3 and raw==bytes.fromhex('cdd863')
 flow=read('ControlFlow');group=next(g for g in flow if g['name']=='Station');instructions=group['instructions'];assert not any(i['address']==0x7F30 for i in instructions)
 evidence=[next(i for i in instructions if i['address']==address) for address in (0x7F1E,0x7F25,0x7F2B,0x7F2E,0x7F2F)]
 assert [i['operation'] for i in evidence]==['PUSH AF','JP Z,#7F33','LD DE,#7F30','PUSH DE','JP (HL)']
 instructions.append(dict(address=0x7F30,operation='CALL #63D8',hex=raw.hex(),slot=4,offset=0x21DC));instructions.sort(key=lambda i:(i['address'],i['slot'],i['offset']))
 group['roots']=sorted(set(group['roots'])|{0x7F30});group['calls']=sorted(set(group['calls'])|{0x63D8});group['instruction_count']+=1;group['code_bytes']+=3;group['classified_fraction']=group['code_bytes']/group['total_bytes']
 block=next(b for b in group['blocks'] if b['slot']==4 and b['offset']<=0x21DC<b['offset']+b['length']);assert block['origin']+0x21DC-block['offset']==0x7F30;block['roots']=sorted(set(block['roots'])|{0x7F30})
 pending[ROOT/'Tools/Disasm/Reports/ControlFlow.json']=encode(flow)
 path='Source/Station/ResumeActionPointer.asm';entry.update(kind='code',path=path,origin=0x7F30);pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encode(source_map)
 text='''                module Station
                module ResumeActionPointer
                ; Документация [созданный на стеке возврат](../../Docs/PackedWordAndActionReturn.md)
                ; In:
                ;   Unknown, точный контракт применяется следующим адресным шагом
Entry:          CALL @Station.ResumePointer.Entry
                ; JP @Station.Unknown7F33.Entry, продолжение в Unknown7F33.asm
                endmodule
                endmodule
''';pending[ROOT/path]=text.encode('utf-8')
 functions=read('Functions');old_total=sum(f['region']=='Station' for f in functions);old_described=sum(f['region']=='Station' and f.get('semantic_status')=='described' for f in functions);assert not any(f['region']=='Station' and f['address']==0x7F30 for f in functions)
 following=next(f for f in functions if f['region']=='Station' and f['address']==0x7F33);new=dict(region='Station',name='ResumeActionPointer',address=0x7F30,slot=4,offset=0x21DC,end_offset=0x21DF,path=path,description='Unknown, вновь выделенный возврат непрямого рисователя',semantic_status='unknown',fallthrough_continuation=0x7F33,fragment_scope='call_then_next_physical_fragment');functions.insert(functions.index(following),new);pending[ROOT/'Tools/Disasm/Reports/Functions.json']=encode(functions)
 symbols=read('Symbols');assert 'Station.ResumeActionPointer.Entry' not in symbols;symbols['Station.ResumeActionPointer.Entry']=0x7F30;pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encode(symbols)
 inventory=read('Inventory');inventory.update(fragments=len(functions),unknown=sum(f.get('semantic_status')!='described' for f in functions),instructions=inventory['instructions']+1);inventory['physical_bytes_by_kind']={k:sum(e['length'] for e in source_map if e['kind']==k) for k in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encode(inventory)
 p=ROOT/'Source/Files/04_STATIONF.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/04_STATIONF/Unclassified043.bin"';assert t.count(needle)==1
 t=t.replace(needle,'                disp #7F30\n                include "../Station/ResumeActionPointer.asm"                   ; (0) жёсткий порядок, последовательное исполнение\n                ent').replace('                include "../Station/Unknown7F33.asm"','                include "../Station/Unknown7F33.asm"                          ; (1) жёсткий порядок, последовательное исполнение');pending[p]=t.encode('utf-8')
 p=ROOT/'Source/Station/HandleItem00.asm';t=p.read_text('utf-8');assert t.count('LD DE, #7F30')==1;t=t.replace('LD DE, #7F30','LD DE, @Station.ResumeActionPointer.Entry').replace('                module HandleItem00\n','                module HandleItem00\n                ; Документация [сохранённый AF и непрямой CPU-возврат](../../Docs/PackedWordAndActionReturn.md)\n');pending[p]=t.encode('utf-8')
 p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');needle='| Station | '+str(old_total)+' | '+str(old_described)+' |';assert t.count(needle)==1;t=t.replace(needle,'| Station | '+str(old_total+1)+' | '+str(old_described)+' |');t+='\n| Адрес | Процедура | Назначение |\n| --- | --- | --- |\n| #7F30 | [Station.ResumeActionPointer](../Source/Station/ResumeActionPointer.asm) | Созданный на стеке возврат непрямого рисователя |\n';pending[p]=t.encode('utf-8')
 p=ROOT/'Docs/FunctionDetails/Station.md';pending[p]=(p.read_text('utf-8')+'\n## ResumeActionPointer\n\n[Station.ResumeActionPointer](../../Source/Station/ResumeActionPointer.asm) — Созданный на стеке возврат непрямого рисователя.\n').encode('utf-8')
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);old=p.read_bytes() if p.exists() else None;plan.append((rel,old,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:assert (ROOT/rel).read_bytes()==old if old is not None else not (ROOT/rel).exists()
 for rel,old,data in plan:
  if old is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
 target=history/oldpath.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 for rel,old,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.read_bytes()==raw==(history/oldpath.relative_to(ROOT)).read_bytes();oldpath.unlink()
 report=dict(passed=True,new_entry=0x7F30,bank=5,slot=4,offset=0x21DC,new_code_bytes=3,new_instructions=1,evidence=evidence,physical_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ActionReturnContinuationDiscovery.json').write_bytes(encode(report));print(json.dumps({k:v for k,v in report.items() if k!='evidence'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
