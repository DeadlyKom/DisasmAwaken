"""Типизация двух физических префиксов, спорные CF08..CF0A не изменяются."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ClipDispatchPrefixData as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_bytes())
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    for stem in ('ActionClipDispatchTable','ActionClipCasesVerification','ActionClipPointWritersVerification','ThreeDOverlayMirrorVerification'):
        assert read(stem)['passed']
    rows=read('ActionClipDispatchTable')['rows'];assert not {3,7}&{r['index'] for r in rows}
    sm,symbols,inventory,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    pending={};removed=[];physical_symbols=0
    for slot,origin,table in facts.TABLES:
        entry=next(e for e in json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())['entries'] if e['slot']==slot)
        source=(ROOT/(entry['path']+'.bin')).read_bytes();start,end=table[2:4]
        assert source[start:end]==bytes.fromhex('D3E488003D7B9500')
        for row in rows:
            if row['index']<8:
                assert row['target']==source[start+row['index']]+256*source[start+256+row['index']]
        old=next(r for r in sm if r['slot']==slot and r['offset']<=start<end<=r['offset']+r['length'])
        assert old['kind']=='unclassified' and old['offset']+old['length']==end
        old_path=ROOT/old['path'];assert old_path.read_bytes()==source[old['offset']:end]
        text,labels=facts.render(source,origin,table);assert facts.parse(text,origin,table)==(source[start:end],labels)
        assert not set(labels)&set(symbols);symbols.update(labels);physical_symbols+=len(labels)
        pending[ROOT/table[1]]=text.encode('utf-8')
        prefix=old['path'].rsplit('/',1)[0]+'/Unclassified'+format(old['offset'],'04X')+'_'+format(start,'04X')+'.bin'
        assert not (ROOT/prefix).exists() and not (ROOT/table[1]).exists();pending[ROOT/prefix]=source[old['offset']:start]
        pieces=[dict(slot=slot,offset=old['offset'],length=start-old['offset'],kind='unclassified',path=prefix,origin=None,sha256=hashlib.sha256(pending[ROOT/prefix]).hexdigest()),
                dict(slot=slot,offset=start,length=8,kind='typed_data',path=table[1],origin=0xCF00,sha256=hashlib.sha256(source[start:end]).hexdigest())]
        sm[sm.index(old):sm.index(old)+1]=pieces
        for item in modified:
            if item.get('target_path')==old['path']:
                assert item['target_slot']==slot;owner=next(p for p in pieces if p['offset']<=item['target_offset']<p['offset']+p['length'])
                item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
        unit=next((ROOT/'Source/Files').glob(format(slot,'02d')+'_*.inc'));text=unit.read_text('utf-8')
        needle='                incbin "../'+old['path'][7:]+'"';assert text.count(needle)==1
        block='\n'.join(('                incbin "../'+prefix[7:]+'"','                assert $ == #'+format(start,'04X'),
            '                ; Документация [префикс таблицы и два рабочих байта](../../Docs/ClipDispatchPrefixData.md)',
            '                disp #CF00','                include "../'+table[1][7:]+'"','                ent'))
        pending[unit]=text.replace(needle,block).encode('utf-8');removed.append((old_path,old_path.read_bytes()))
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm));inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');assert 'struct FClipDispatchPrefix' not in text
    pending[p]=text.replace('                endif',facts.structure()+'\n                endif').encode('utf-8')
    p=ROOT/'Includes/Variables/Include.inc';text=p.read_text('utf-8')
    for name,address in (('CornerBlock',0xCF03),('SeenFlags',0xCF07)):
        lines=[];found=0
        for line in text.splitlines():
            if line.startswith(name.ljust(16)+'equ #'+format(address,'04X')):
                line+='\n                assert '+name+' == @ActionClipDispatchPrefix.Value.'+name;found+=1
            lines.append(line)
        assert found==1,(name,found);text='\n'.join(lines)+'\n'
    pending[p]=text.encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка двух физических префиксов CF00, CF08 остаётся отдельным спорным диапазоном.
    from ClipDispatchPrefixData import TABLES as CLIP_PREFIX_TABLES, parse as parse_clip_prefix
    for slot,origin,table in CLIP_PREFIX_TABLES:
        raw,labels=parse_clip_prefix((ROOT/table[1]).read_text('utf-8'),origin,table)
        assert raw==sources[slot][table[2]:table[3]]==bytes.fromhex('D3E488003D7B9500')
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        rows=[p for p in source_map if p['path']==table[1]]
        assert len(rows)==1 and (rows[0]['slot'],rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(slot,table[2],8,0xCF00)
        assert symbols['FCLIPDISPATCHPREFIX']==8
        for i,(field,width,meaning) in enumerate(table[5]):assert symbols[('FClipDispatchPrefix.'+field).upper()]==i
    assert symbols['ACTIONCLIPPOINTWRITERSSTATE.CORNERBLOCK']==symbols['ACTIONCLIPDISPATCHPREFIX.VALUE.CORNERBLOCK']
    assert symbols['ACTIONCLIPCASESSTATE.SEENFLAGS']==symbols['ACTIONCLIPDISPATCHPREFIX.VALUE.SEENFLAGS']

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Раздельные физические копии префикса таблицы отсечения, без переклассификации CF08.
    from ClipDispatchPrefixData import TABLES as CLIP_PREFIX_TABLES, render as render_clip_prefix
    for slot,origin,table in CLIP_PREFIX_TABLES:
        prefix_text,prefix_labels=render_clip_prefix(data_by_slot[slot],origin,table)
        write(table[1],prefix_text);symbols.update(prefix_labels)
        special[slot,table[2]]=(table[3],table[1],0xCF00)

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ClipDispatchPrefixData';history=ROOT/'Tools/Disasm/Research/History/BeforeClipDispatchPrefixData'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
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
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='clip-prefix-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    for p,data in removed:
        assert p.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
        assert p.read_bytes()==data==(history/p.relative_to(ROOT)).read_bytes();p.unlink()
    result=dict(passed=True,typed_bytes=16,physical_records=2,physical_symbols=physical_symbols,
        six_target_low_bytes_and_two_work_bytes_per_record=True,valid_pair_indices_exclude_03_and_07=True,
        physical_slots_checked=[17,19],original_bytes_and_instructions_preserved=True,
        cf08_reclassified=False,cf08_execution_entry_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ClipDispatchPrefixDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
