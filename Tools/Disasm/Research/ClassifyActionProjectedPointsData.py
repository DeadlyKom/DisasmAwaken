"""Физическая типизация 40 результатов исходных моделей без изменения размещения."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionProjectedPointsData as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_bytes())
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionObjectVerticesVerification');assert proof['passed'] and proof['maximum_original_points']==40 and proof['original_even_pointers']==128
    assert read('ActionVertexCodesVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();sm,symbols,inventory,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    start,end=facts.TABLE[2:4];old=next(r for r in sm if r['slot']==17 and r['offset']<=start<end<=r['offset']+r['length'])
    assert old['kind']=='unclassified';old_path=ROOT/old['path'];old_end=old['offset']+old['length']
    assert old_path.read_bytes()==source[old['offset']:old_end]
    text,labels=facts.render(source);assert facts.parse(text)==(source[start:end],labels)
    assert not set(labels)&set(symbols);symbols.update(labels);pending={ROOT/facts.TABLE[1]:text.encode('utf-8')};pieces=[]
    for begin,finish,path,kind in ((old['offset'],start,f'Source/Resources/17_ACTION/Unclassified{old["offset"]:04X}_{start:04X}.bin','unclassified'),
        (start,end,facts.TABLE[1],'typed_data'),(end,old_end,f'Source/Resources/17_ACTION/Unclassified{end:04X}_{old_end:04X}.bin','unclassified')):
        assert finish>begin and not (ROOT/path).exists();raw=source[begin:finish]
        if kind=='unclassified':pending[ROOT/path]=raw
        pieces.append(dict(slot=17,offset=begin,length=finish-begin,kind=kind,path=path,origin=begin+0x6000 if kind=='typed_data' else None,sha256=hashlib.sha256(raw).hexdigest()))
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm));inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==old['path']:
            assert item['target_slot']==17;owner=next(r for r in pieces if r['offset']<=item['target_offset']<r['offset']+r['length'])
            item['target_path']=owner['path'];item['target_source_classified']=owner['kind']!='unclassified'
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    p=ROOT/'Source/Files/17_ACTION.inc';text=p.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=['                ; Документация [физические ячейки проекции](../../Docs/ActionProjectedPointsData.md)']
    for r in pieces:
        lines+=['                assert $ == #'+format(r['offset'],'04X')]
        if r['kind']=='typed_data':lines+=['                disp #8E00','                include "../Action/Data/ProjectedPoints.asm"','                ent']
        else:lines+=['                ; Unknown, соседняя рабочая память не классифицирована этой типизацией','                incbin "../'+r['path'][7:]+'"']
    pending[p]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка физических ячеек пятибайтового результата исходных моделей ACTION.
    from ActionProjectedPointsData import TABLE as PROJECTED_POINTS_TABLE, parse as parse_projected_points
    raw,labels=parse_projected_points((ROOT/PROJECTED_POINTS_TABLE[1]).read_text('utf-8'))
    assert raw==sources[17][0x2E00:0x2EC8]
    assert all(symbols.get(k.upper())==v for k,v in labels.items())
    assert symbols['FRENDERPROJECTEDPOINT']==5 and symbols['FRENDERPROJECTEDPOINT.SECOND']==0
    assert symbols['FRENDERPROJECTEDPOINT.FIRST']==2 and symbols['FRENDERPROJECTEDPOINT.CLIPCODE']==4
    assert symbols['ACTIONVERTEXGROUPCONST.WORKPAGE']==labels['ActionProjectedPoints.Point00']
    rows=[p for p in source_map if p['path']==PROJECTED_POINTS_TABLE[1]]
    assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(0x2E00,200,0x8E00)

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические ячейки результата проекции, предел исходных моделей не является ограничителем кода.
    from ActionProjectedPointsData import TABLE as PROJECTED_POINTS_TABLE, render as render_projected_points
    projected_text,projected_labels=render_projected_points(data_by_slot[17])
    write(PROJECTED_POINTS_TABLE[1],projected_text);symbols.update(projected_labels)
    special[17,0x2E00]=(0x2EC8,PROJECTED_POINTS_TABLE[1],0x8E00)

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionProjectedPointsData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionProjectedPointsData'
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
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='projected-points-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[old['offset']:old_end]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,typed_bytes=200,physical_records=40,physical_symbols=len(labels),original_even_model_pointers=128,
        initial_disk_bytes_preserved=True,existing_structure_reused=True,consumer_instructions_preserved=True,
        projection_preserves_clip_code=True,arbitrary_runtime_capacity_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectedPointsDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
