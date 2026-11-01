"""Одноразовое выделение доказанных 294 байтов текстов приветствия без изменения размещения."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from Analyze import payload


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('WelcomePanelVerification')['passed'];source=payload(4);source_map=read('SourceMap')
 old=next(e for e in source_map if e['slot']==4 and e['offset']==0x6CF3);oldpath=ROOT/old['path'];raw=oldpath.read_bytes()
 assert old['kind']=='unclassified' and old['length']==0x832E-0x6CF3 and raw==source[0x6CF3:0x832E]
 candidate=ROOT/'Tools/Disasm/Research/Candidates/WelcomeTextDataScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeWelcomeTextData';assert not candidate.exists() and not history.exists()
 pieces=((0x6CF3,0x6D82,'WelcomeModelLabels.bin','binary_resource'),(0x6D82,0x6E19,'WelcomeTemplate.bin','binary_resource'),(0x6E19,0x832E,'Unclassified085AfterWelcome.bin','unclassified'))
 pending={};entries=[]
 for start,end,name,kind in pieces:
  path='Source/Resources/04_STATIONF/'+name;data=source[start:end];assert not (ROOT/path).exists();pending[ROOT/path]=data
  entries.append(dict(slot=4,offset=start,length=end-start,kind=kind,path=path,origin=None,sha256=hashlib.sha256(data).hexdigest()))
 assert b''.join(pending[ROOT/e['path']] for e in entries)==raw
 index=source_map.index(old);source_map[index:index+1]=entries;pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encoded(source_map)
 p=ROOT/'Source/Files/04_STATIONF.inc';text=p.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/04_STATIONF/Unclassified085.bin"';assert text.count(needle)==1
 block='''                ; Документация [тексты приветствия](../../Docs/WelcomePanel.md)
                ; LF перед шестнадцатью исходными подписями моделей станции, адрес CCF3
                incbin "../Resources/04_STATIONF/WelcomeModelLabels.bin"
                assert $ == #6D82
                ; четыре части шаблона, первые три заканчиваются кодом вставки 01, адрес CD82
                incbin "../Resources/04_STATIONF/WelcomeTemplate.bin"
                assert $ == #6E19
                ; Unknown, остальные сообщения и данные ещё требуют отдельного разбора
                incbin "../Resources/04_STATIONF/Unclassified085AfterWelcome.bin"'''
 pending[p]=text.replace(needle,block).encode('utf-8')
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in inventory['physical_bytes_by_kind']};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
 records=[];cursor=0x6CF4
 assert source[0x6CF3]==10
 for ordinal in range(1,17):
  end=source.index(10,cursor);records.append(dict(model=ordinal,address=0x6000+cursor,length=end+1-cursor,text=source[cursor:end].decode('cp866')));cursor=end+1
 assert cursor==0x6D82 and source[0x6D82:0x6E19].count(1)==3 and source[0x6E18]==10
 pending[ROOT/'Tools/Disasm/Reports/WelcomeTextLayout.json']=encoded(dict(passed=True,model_records=records,template_address=0xCD82,template_size=151,classified_bytes=294,remaining_unknown_bytes=0x832E-0x6E19,original_bytes_preserved=True,assembly_executed=False))
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;plan.append((rel,before,data));q=candidate/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()
 for rel,before,data in plan:
  if before is not None:q=history/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
 q=history/oldpath.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
 for rel,before,data in plan:q=ROOT/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.resolve().is_relative_to((ROOT/'Source/Resources/04_STATIONF').resolve()) and oldpath.read_bytes()==raw==(history/oldpath.relative_to(ROOT)).read_bytes();oldpath.unlink()
 result=dict(passed=True,classified_resource_bytes=294,model_labels=16,template_parts=4,original_bytes_preserved=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/WelcomeTextDataClassification.json').write_bytes(encoded(result));print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
