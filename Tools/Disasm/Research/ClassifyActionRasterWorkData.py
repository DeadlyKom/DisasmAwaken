"""Публикация шести физических байтов состояния линии без изменения инструкций."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionRasterWorkData as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_bytes())
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    assert source[0x2D2A:0x2D2E]==bytes(4) and source[0x2D4E:0x2D50]==bytes(2)
    assert read('ActionLineRasterVerification')['passed']
    sm,symbols,inventory,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    old=next(r for r in sm if r['slot']==17 and r['offset']<=0x2D2A<0x2D50<=r['offset']+r['length'])
    assert old['kind']=='unclassified' and old['length']==512
    old_path=ROOT/old['path'];old_end=old['offset']+old['length'];assert old_path.read_bytes()==source[old['offset']:old_end]
    pending={};pieces=[];cursor=old['offset'];new_labels={}
    for table in facts.TABLES:
        start,end=table[2:4]
        if cursor<start:
            relative=f'Source/Resources/17_ACTION/Unclassified{cursor:04X}_{start:04X}.bin'
            raw=source[cursor:start];pending[ROOT/relative]=raw
            pieces.append(dict(slot=17,offset=cursor,length=len(raw),kind='unclassified',path=relative,origin=None,sha256=hashlib.sha256(raw).hexdigest()))
        text,labels=facts.render(source,table);raw,parsed=facts.parse(text,table);assert parsed==labels and raw==source[start:end]
        assert not set(labels)&(set(symbols)|set(new_labels));new_labels.update(labels)
        pending[ROOT/table[1]]=text.encode('utf-8')
        pieces.append(dict(slot=17,offset=start,length=end-start,kind='typed_data',path=table[1],origin=start+0x6000,sha256=hashlib.sha256(raw).hexdigest()))
        cursor=end
    if cursor<old_end:
        relative=f'Source/Resources/17_ACTION/Unclassified{cursor:04X}_{old_end:04X}.bin';raw=source[cursor:old_end];pending[ROOT/relative]=raw
        pieces.append(dict(slot=17,offset=cursor,length=len(raw),kind='unclassified',path=relative,origin=None,sha256=hashlib.sha256(raw).hexdigest()))
    assert all(not p.exists() for p in pending)
    symbols.update(new_labels);sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm))
    inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==old['path']:
            assert item['target_slot']==17
            owner=next(r for r in pieces if r['offset']<=item['target_offset']<r['offset']+r['length'])
            item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    p=ROOT/'Source/Files/17_ACTION.inc';text=p.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=['                ; Документация [физические входные состояния](../../Docs/ActionRasterWorkData.md)']
    for r in pieces:
        lines+=['                assert $ == #'+format(r['offset'],'04X')]
        if r['kind']=='typed_data':lines+=['                disp #'+format(r['origin'],'04X'),'                include "../'+r['path'][7:]+'"','                ent']
        else:lines+=['                ; Unknown, соседнее состояние требует отдельного разбора','                incbin "../'+r['path'][7:]+'"']
    pending[p]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');assert 'struct FLineRasterPoint' not in text and 'struct FLineRasterMode' not in text
    pending[p]=text.replace('                endif',facts.structures()+'\n                endif').encode('utf-8')
    p=ROOT/'Includes/Variables/Include.inc';text=p.read_text('utf-8')
    for alias,address,target in (('FirstPoint',0x8D2A,'ActionRasterPoints.FirstPoint'),('SecondPoint',0x8D2C,'ActionRasterPoints.SecondPoint'),
        ('PixelOpcode',0x8D4E,'ActionRasterMode.Value.PixelOpcode'),('BranchOpcode',0x8D4F,'ActionRasterMode.Value.BranchOpcode')):
        lines=[];found=0
        for line in text.splitlines():
            if line.startswith(alias.ljust(16)+'equ #'+format(address,'04X')):
                line+='\n                assert '+alias+' == @'+target;found+=1
            lines.append(line)
        assert found==1,(alias,found);text='\n'.join(lines)+'\n'
    pending[p]=text.encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка физических упакованных концов линии и полных кодов режима.
    from ActionRasterWorkData import TABLES as INPUT_CONTEXT_TABLES, parse as parse_input_context
    for table in INPUT_CONTEXT_TABLES:
        raw,labels=parse_input_context((ROOT/table[1]).read_text('utf-8'),table)
        assert raw==sources[17][table[2]:table[3]]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        rows=[p for p in source_map if p['path']==table[1]]
        assert len(rows)==1 and rows[0]['kind']=='typed_data'
        assert (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(table[2],table[3]-table[2],table[2]+0x6000)
    for alias,target in (('FirstPoint','ActionRasterPoints.FirstPoint'),('SecondPoint','ActionRasterPoints.SecondPoint'),
                         ('PixelOpcode','ActionRasterMode.Value.PixelOpcode'),('BranchOpcode','ActionRasterMode.Value.BranchOpcode')):
        assert symbols[('ActionLineRasterState.'+alias).upper()]==symbols[target.upper()]
    assert symbols['FLINERASTERPOINT']==2 and symbols['FLINERASTERMODE']==2
    assert symbols['FLINERASTERPOINT.SECOND']==0 and symbols['FLINERASTERPOINT.FIRST']==1
    assert symbols['FLINERASTERMODE.PIXELOPCODE']==0 and symbols['FLINERASTERMODE.BRANCHOPCODE']==1

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические упакованные точки и выбор команд линейного растеризатора.
    from ActionRasterWorkData import TABLES as INPUT_CONTEXT_TABLES, render as render_input_context
    for table in INPUT_CONTEXT_TABLES:
        input_text,input_labels=render_input_context(data_by_slot[17],table)
        write(table[1],input_text);symbols.update(input_labels)
        special[17,table[2]]=(table[3],table[1],table[2]+0x6000)

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionRasterWorkData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionRasterWorkData'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    q=history/old_path.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(old_path.read_bytes())
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='input-context-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[old['offset']:old_end]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,typed_bytes=6,physical_records=3,physical_symbols=len(new_labels),aliases_bound_to_physical_fields=4,
        original_addresses_and_bytes_preserved=True,consumer_instructions_preserved=True,
        new_gameplay_semantics_inferred=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRasterWorkDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
