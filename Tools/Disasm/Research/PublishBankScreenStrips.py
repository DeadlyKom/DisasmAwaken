"""Публикация физических заголовков и растров BANK, неизвестные промежутки сохраняются."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
import BankScreenStrips as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
import VerifySources


def main():
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('BankScreenStripsVerification');assert proof['passed'] and proof['wrong_height_probe_rejected']
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    sources={slot:(ROOT/('Tools/Disasm/Extracted/Active/'+str(slot)+'_BANK'+str(slot-33)+'.C.bin')).read_bytes() for slot in facts.SLOTS}
    tables=facts.tables(sources);pending={};removed=[]
    for table in tables:
        text,labels,bitmaps=facts.render(sources[table['slot']],table)
        assert facts.parse(text,table,bitmaps)==(sources[table['slot']][table['start']:table['end']],labels)
        assert not set(labels)&set(symbols);symbols.update(labels)
        for path,data in bitmaps.items():assert not (ROOT/path).exists();pending[ROOT/path]=data
        p=ROOT/table['path'];assert not p.exists();pending[p]=text.encode('utf-8')
    for slot in facts.SLOTS:
        rows=[r for r in source_map if r['slot']==slot];assert len(rows)==1
        old=rows[0];assert old['kind']=='unclassified' and old['offset']==0 and old['length']==16384
        old_path=ROOT/old['path'];data=sources[slot];assert old_path.read_bytes()==data
        assert not any(row.get('target_path')==old['path'] for row in read('ModifiedCode'))
        groups=[t for t in tables if t['slot']==slot];layout=facts.analyze(data)
        gap_path='Source/Resources/'+str(slot)+'_BANK'+str(slot-33)+'/UnknownGap.bin'
        assert not (ROOT/gap_path).exists();pending[ROOT/gap_path]=data[layout['gap_start']:layout['gap_end']]
        pieces=[]
        for start,end,path,kind in ((0,layout['gap_start'],groups[0]['path'],'typed_data'),
            (layout['gap_start'],layout['gap_end'],gap_path,'unclassified'),
            (layout['gap_end'],16384,groups[1]['path'],'typed_data')):
            row=dict(slot=slot,offset=start,length=end-start,path=path,kind=kind,origin=None,
                     sha256=hashlib.sha256(data[start:end]).hexdigest())
            if kind=='typed_data':row['format']='BANK48_SCREEN_STRIPS'
            pieces.append(row)
        index=source_map.index(old);source_map[index:index+1]=pieces
        p=ROOT/('Source/Files/'+str(slot)+'_BANK'+str(slot-33)+'.inc');text=p.read_text('utf-8')
        needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../'+old['path'][7:]+'"'
        assert text.count(needle)==1
        lines=['                ; Документация [графические цепочки и неизвестный промежуток](../../Docs/BankScreenStrips.md)']
        for row in pieces:
            lines.append('                assert $ == #'+format(row['offset'],'04X'))
            if row['kind']=='typed_data':lines.append('                include "../'+row['path'][7:]+'"')
            else:
                lines.append('                ; Unknown, содержимое промежутка не объявляется неиспользуемым')
                lines.append('                incbin "../'+row['path'][7:]+'"')
        pending[p]=text.replace(needle,'\n'.join(lines)).encode('utf-8');removed.append((old_path,data))
    inventory['ranges_by_kind']=dict(Counter(row['kind'] for row in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(row['length'] for row in source_map if row['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[reports/(name+'.json')]=encode(value)
    p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8')
    assert 'struct '+facts.STRUCTURE not in text and text.count('                endif')==1
    pending[p]=text.replace('                endif',facts.structures()+'\n                endif').encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook=('    # Проверка реальных заголовков, всех растров и сохранённых промежутков BANK.\n'
          '    from BankScreenStrips import verify_published as verify_bank_screen_strips\n'
          '    verify_bank_screen_strips(sources,source_map,symbols)\n\n')
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8')
    needle='    binary_resources[7, 0x2900]';assert text.count(needle)==1
    hook='''    # Файловые смещения графических контейнеров BANK не являются адресами загрузки.
    from BankScreenStrips import tables as bank_strip_tables, render as render_bank_strips
    bank_strip_resources={}
    for table in bank_strip_tables(data_by_slot):
        header_text,header_labels,bitmaps=render_bank_strips(data_by_slot[table['slot']],table)
        write(table['path'],header_text);symbols.update(header_labels)
        for bitmap_path,bitmap_data in bitmaps.items():
            target=ROOT/bitmap_path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(bitmap_data)
        bank_strip_resources[table['slot'],table['start']]=(table['end'],table['path'])
'''
    text=text.replace(needle,hook+needle)
    needle='            if (slot, offset) in binary_resources:';assert text.count(needle)==1
    hook='''            if (slot,offset) in bank_strip_resources:
                end,path=bank_strip_resources[slot,offset]
                lines.extend([asm(f"assert $ == #{offset:04X}"),asm('include "../'+path[7:]+'"')])
                source_map.append(dict(slot=slot,offset=offset,length=end-offset,kind='typed_data',path=path,
                    origin=None,format='BANK48_SCREEN_STRIPS',sha256=hashlib.sha256(data[offset:end]).hexdigest()))
                offset=end
                continue
'''
    text=text.replace(needle,hook+needle)
    needle='and (slot, offset) not in special and (slot, offset) not in binary_resources):';assert text.count(needle)==1
    text=text.replace(needle,'and (slot, offset) not in special and (slot, offset) not in binary_resources and (slot, offset) not in bank_strip_resources):')
    needle='                path = ROOT / binary_path';assert text.count(needle)==1
    text=text.replace(needle,"                if slot in range(33,39):binary_path=f'Source/Resources/{slot}_BANK{slot-33}/UnknownGap.bin'\n"+needle)
    pending[p]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/BankScreenStrips';history=ROOT/'Tools/Disasm/Research/History/BeforeBankScreenStrips'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,data in removed:
        q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='bank-strip-source-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
    for p,data in removed:
        assert p.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
        assert p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
    result=dict(passed=True,record_count=166,graphic_bytes_classified=86874,header_bytes=498,bitmap_bytes=86376,
        unknown_gap_bytes_preserved=11430,original_bytes_and_physical_layout_preserved=True,
        labels_are_file_offsets=True,hardware_bank_numbers_assigned=False,runtime_loader_proved=False,
        paired_records_temporal_relation_proved=False,python_needed_for_ordinary_build=False,
        assembly_executed=False,native_execution=False)
    (reports/'BankScreenStripsClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
