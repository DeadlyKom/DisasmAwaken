"""Выделение полных копий растров из промежутков BANK4 и BANK5 без изменения остальных ресурсов."""
from collections import Counter
import contextlib,hashlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
import BankScreenStrips as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
import VerifySources


def main():
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('AdditionalBankStripsVerification');assert proof['passed'] and proof['complete_header_and_bitmap_copies']
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    sources={slot:(ROOT/('Tools/Disasm/Extracted/Active/'+str(slot)+'_BANK'+str(slot-33)+'.C.bin')).read_bytes() for slot in facts.SLOTS}
    pending={};removed=[]
    for table in facts.additional_tables(sources):
        slot=table['slot'];data=sources[slot];text,labels,bitmaps=facts.render(data,table)
        assert facts.parse(text,table,bitmaps)==(data[table['start']:table['end']],labels)
        assert not set(labels)&set(symbols);symbols.update(labels)
        for path,blob in bitmaps.items():assert not (ROOT/path).exists();pending[ROOT/path]=blob
        p=ROOT/table['path'];assert not p.exists();pending[p]=text.encode('utf-8')
        old=next(r for r in source_map if r['slot']==slot and r['kind']=='unclassified')
        first,last=old['offset'],old['offset']+old['length'];assert first<table['start']<table['end']<last
        old_path=ROOT/old['path'];before=old_path.read_bytes();assert before==data[first:last]
        assert not any(row.get('target_path')==old['path'] for row in read('ModifiedCode'))
        spans=[]
        for start,end,kind in ((first,table['start'],'unclassified'),(table['start'],table['end'],'typed_data'),(table['end'],last,'unclassified')):
            if kind=='typed_data':path=table['path']
            else:
                path=old['path'].rsplit('/',1)[0]+'/UnknownGap'+format(start,'04X')+'_'+format(end,'04X')+'.bin'
                assert not (ROOT/path).exists();pending[ROOT/path]=data[start:end]
            spans.append(dict(slot=slot,offset=start,length=end-start,path=path,kind=kind,origin=None,
                sha256=hashlib.sha256(data[start:end]).hexdigest()))
        index=source_map.index(old);source_map[index:index+1]=spans
        p=ROOT/('Source/Files/'+str(slot)+'_BANK'+str(slot-33)+'.inc');unit=p.read_text('utf-8')
        needle='                incbin "../'+old['path'][7:]+'"';assert unit.count(needle)==1
        lines=[]
        for row in spans:
            lines.append('                assert $ == #'+format(row['offset'],'04X'))
            if row['kind']=='typed_data':lines.append('                include "../'+row['path'][7:]+'"')
            else:
                lines.append('                ; Unknown, оставшаяся часть промежутка сохраняется буквально')
                lines.append('                incbin "../'+row['path'][7:]+'"')
        pending[p]=unit.replace(needle,'\n'.join(lines)).encode('utf-8');removed.append((old_path,before))
    inventory['ranges_by_kind']=dict(Counter(row['kind'] for row in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(row['length'] for row in source_map if row['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[reports/(name+'.json')]=encode(value)
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8')
    needle='from BankScreenStrips import tables as bank_strip_tables';assert text.count(needle)==1
    text=text.replace(needle,'from BankScreenStrips import all_tables as bank_strip_tables')
    needle='    for table in bank_strip_tables(data_by_slot):';assert text.count(needle)==1
    text=text.replace(needle,"    bank_strip_definitions=bank_strip_tables(data_by_slot)\n    bank_strip_additional_slots={t['slot'] for t in bank_strip_definitions if t['module'].endswith('Additional')}\n    for table in bank_strip_definitions:")
    needle="                if slot in range(33,39):binary_path=f'Source/Resources/{slot}_BANK{slot-33}/UnknownGap.bin'";assert text.count(needle)==1
    replacement="""                if slot in range(33,39):
                    gap_name=f'UnknownGap{begin:04X}_{offset:04X}.bin' if slot in bank_strip_additional_slots else 'UnknownGap.bin'
                    binary_path=f'Source/Resources/{slot}_BANK{slot-33}/'+gap_name"""
    pending[p]=text.replace(needle,replacement).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/AdditionalBankStrips';history=ROOT/'Tools/Disasm/Research/History/BeforeAdditionalBankStrips'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before in removed:
        q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='additional-strip-source-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    for p,before in removed:
        assert p.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
        assert p.read_bytes()==before==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
    result=dict(passed=True,additional_records=4,additional_graphic_bytes=2172,remaining_bank_gap_bytes=9258,
        original_bytes_and_layout_preserved=True,previously_published_strip_labels_preserved=True,
        runtime_reachability_proved=False,unused_or_garbage_asserted=False,
        python_needed_for_ordinary_build=False,assembly_executed=False,native_execution=False)
    (reports/'AdditionalBankStripsClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
