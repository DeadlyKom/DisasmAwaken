"""Одноразовое оформление девяти исходных байтов общего имени SAVE1 в FTrDosFileKey."""
from pathlib import Path
import collections,contextlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from Analyze import payload


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(n):return json.loads((ROOT/('Tools/Disasm/Reports/'+n+'.json')).read_text('utf-8'))
 def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('SaveSlotProtocolVerification')['passed'];source=payload(4);data=source[0x17DC:0x17E5];assert data==b'SAVE1   s'
 candidate=ROOT/'Tools/Disasm/Research/Candidates/SaveSlotFileKeyScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeSaveSlotFileKey';assert not candidate.exists() and not history.exists()
 source_map=read('SourceMap');entry=next(e for e in source_map if e['slot']==4 and e['offset']==0x17DC);oldpath=ROOT/entry['path'];assert entry['length']==9 and oldpath.read_bytes()==data
 path='Source/Station/Data/SaveSlotFileName.asm';text='''                module SaveSlotFileName
                ; Документация [сохранения слотов](../../../Docs/SaveSlots.md)
                ; проверка исходного адреса физического ключа SAVE
                assert $ == #7530
Entry:          FTrDosFileKey { { "SAVE1   " }, #73 }                           ; Name содержит SAVE, цифру и три пробела, Extension=s
                ; проверка конца девятибайтового имени и типа
                assert $ == #7539
                endmodule
''';pending={ROOT/path:text.encode('utf-8')};entry.update(kind='typed_data',path=path,origin=0x7530);pending[ROOT/'Tools/Disasm/Reports/SourceMap.json']=encoded(source_map)
 symbols=read('Symbols');assert 'SaveSlotFileName.Entry' not in symbols;symbols.update({'SaveSlotFileName.Entry':0x7530,'SaveSlotFileName.Entry.Name':0x7530,'SaveSlotFileName.Entry.Extension':0x7538});pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=encoded(symbols)
 p=ROOT/'Source/Files/04_STATIONF.inc';t=p.read_text('utf-8');needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/04_STATIONF/Unclassified033.bin"';assert t.count(needle)==1
 pending[p]=t.replace(needle,'                disp #7530\n                include "../Station/Data/SaveSlotFileName.asm"\n                ent').encode('utf-8')
 p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    # Проверка физического имени FINALF в перенесённом финальном выходе.';assert t.count(needle)==1
 check='''    # Проверка исходного общего имени SAVE1 как физического FTrDosFileKey.
    save_slot_file_keys = 0
    path = "Source/Station/Data/SaveSlotFileName.asm"
    entries = [item for item in source_map if item['path'] == path]
    if entries:
        if len(entries) != 1 or (entries[0]['slot'], entries[0]['offset'], entries[0]['length'], entries[0]['origin']) != (4, 0x17DC, 9, 0x7530):
            raise ValueError('Изменилось размещение ключа SAVE1')
        text = (ROOT / path).read_text(encoding='utf-8')
        found = re.findall(r'FTrDosFileKey\\s*\\{\\s*\\{\\s*"([^"]*)"\\s*\\}\\s*,\\s*#([0-9A-Fa-f]+)\\s*\\}', text)
        if len(found) != 1 or len(found[0][0]) != 8:
            raise ValueError('Не найден физический ключ SAVE1')
        raw = found[0][0].encode('ascii') + bytes([int(found[0][1], 16)])
        if raw != sources[4][0x17DC:0x17E5] or symbols.get('SAVESLOTFILENAME.ENTRY') != 0x7530:
            raise ValueError('Изменились имя, тип либо адрес ключа SAVE1')
        save_slot_file_keys = 1

''';t=t.replace(needle,check+needle);t=t.replace('action_file_keys=action_file_keys, final_file_keys=final_file_keys','action_file_keys=action_file_keys, save_slot_file_keys=save_slot_file_keys, final_file_keys=final_file_keys');pending[p]=t.encode('utf-8')
 inv=read('Inventory');inv['physical_bytes_by_kind']={kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in inv['physical_bytes_by_kind']};inv['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map));pending[ROOT/'Tools/Disasm/Reports/Inventory.json']=encoded(inv)
 plan=[]
 for p,new in pending.items():
  rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;plan.append((rel,before,new));q=candidate/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(new)
 for rel,before,new in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()
 for rel,before,new in plan:
  if before is not None:q=history/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
 q=history/oldpath.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
 for rel,before,new in plan:q=ROOT/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(new)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert oldpath.resolve().is_relative_to((ROOT/'Source/Resources/04_STATIONF').resolve()) and oldpath.read_bytes()==data==(history/oldpath.relative_to(ROOT)).read_bytes();oldpath.unlink()
 result=dict(passed=True,typed_bytes=9,physical_file_key_records=1,original_bytes_preserved=True,assembly_executed=False);(ROOT/'Tools/Disasm/Reports/SaveSlotFileKeyClassification.json').write_bytes(encoded(result));print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
