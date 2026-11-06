"""Физические точки и переход с адресных псевдонимов на настоящие поля STRUCT."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionClipPointsData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionSingleEdgeVerification')['all_physical_ram_bytes_proved'] and read('ActionPolygonVerification')['all_physical_ram_bytes_proved']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();sm,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    old=next(i for i in sm if i['slot']==17 and i['offset']==0x6F0B);assert old['length']==32 and old['kind']=='unclassified'
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x6F0B:0x6F2B]
    pending={};pieces=((0x6F0B,0x6F10,facts.POINTS[0][2],True),(0x6F10,0x6F1B,'Source/Resources/17_ACTION/Unclassified027_BetweenClipPoints.bin',False),
        (0x6F1B,0x6F20,facts.POINTS[1][2],True),(0x6F20,0x6F2B,'Source/Resources/17_ACTION/Unclassified027_AfterClipPoints.bin',False))
    for name,offset,path in facts.POINTS:
        text,labels=facts.render(source,name,offset);assert facts.parse(text,name,offset)==(source[offset:offset+5],labels)
        assert not set(labels)&set(symbols);symbols.update(labels);pending[ROOT/path]=text.encode('utf-8')
    ranges=[]
    for start,end,path,typed in pieces:
        if not typed:pending[ROOT/path]=source[start:end]
        ranges.append(dict(slot=17,offset=start,length=end-start,kind='typed_data' if typed else 'unclassified',path=path,
            origin=start+0x6000 if typed else None,sha256=hashlib.sha256(source[start:end]).hexdigest()))
    at=sm.index(old);sm[at:at+1]=ranges
    inventory['ranges_by_kind']=dict(Counter(x['kind'] for x in sm));inventory['physical_bytes_by_kind']={kind:sum(x['length'] for x in sm if x['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    p=ROOT/'Source/Files/17_ACTION.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert t.count(needle)==1;lines=[]
    for start,end,path,typed in pieces:
        lines+=['                assert $ == #'+format(start,'04X')]
        if typed:lines+=['                disp #'+format(start+0x6000,'04X'),'                include "../Action/Data/'+path.rsplit('/',1)[-1]+'"','                ent']
        else:lines+=['                ; Соседние байты таблицы, поэлементная разметка ещё не оформлена','                incbin "../Resources/17_ACTION/'+path.rsplit('/',1)[-1]+'"']
    pending[p]=t.replace(needle,'\n'.join(lines)).encode('utf-8')
    # Переход только подтверждённых обращений к полям физических точек.
    for p in (ROOT/'Source/Action').rglob('*.asm'):
        before=p.read_text('utf-8');after=before
        for point in ('FirstPoint','SecondPoint'):after=after.replace('@ActionClipProductsState.'+point+'+FRenderProjectedPoint.','@ActionClipPoints.'+point+'.')
        if after!=before:pending[p]=after.encode('utf-8')
    for filename in ('ActionClipProductsFacts.py','ActionClipIntersectionsFacts.py','ActionClipComparisonsFacts.py','ActionClipPointWritersFacts.py','ActionPolygonFacts.py','ActionSingleEdgeFacts.py'):
        p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');needle='    return operation';assert t.count(needle)==1
        extra="    for point in ('FirstPoint','SecondPoint'):\n        operation=operation.replace('@ActionClipProductsState.'+point+'+FRenderProjectedPoint.','@ActionClipPoints.'+point+'.')\n"
        pending[p]=t.replace(needle,extra+needle).encode('utf-8')
    p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');start=t.index('                module ActionClipProductsState');end=t.index('                endmodule',start)+len('                endmodule\n')
    block=t[start:end];assert 'FirstPoint' in block and 'SecondPoint' in block
    assert not any('equ ' in line and not line.startswith(('FirstPoint','SecondPoint')) for line in block.splitlines())
    pending[p]=(t[:start]+t[end:]).encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.';assert t.count(needle)==1
    hook='''    # Проверка двух физических точек, их вложенных координат и кода, а не только адресных EQU.
    from ActionClipPointsData import POINTS as CLIP_POINTS, parse as parse_clip_point
    for name,offset,path in CLIP_POINTS:
        point_raw,point_labels=parse_clip_point((ROOT/path).read_text('utf-8'),name,offset)
        assert point_raw==sources[17][offset:offset+5]
        assert all(symbols.get(k.upper())==v for k,v in point_labels.items())
        items=[x for x in source_map if x['path']==path]
        assert len(items)==1 and (items[0]['offset'],items[0]['length'],items[0]['origin'])==(offset,5,offset+0x6000)
    assert symbols['FRENDERPROJECTEDPOINT']==5 and symbols['FRENDERPROJECTEDPOINT.CLIPCODE']==4

'''
    pending[p]=t.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';t=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert t.count(needle)==1
    hook='''    # Физические рабочие точки внутри невыбираемых индексов младшей таблицы ACTION.
    from ActionClipPointsData import POINTS as CLIP_POINTS, render as render_clip_point
    for name,offset,path in CLIP_POINTS:
        text,bindings=render_clip_point(data_by_slot[17],name,offset)
        write(path,text);symbols.update(bindings)
        special[17,offset]=(offset+5,path,offset+0x6000)
'''
    pending[p]=t.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionClipPointsData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionClipPointsData';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for p,before,data in plan:
        c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
    for p,before,data in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,data in plan:
        if before is not None:
            h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(before)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    backup=history/old_path.relative_to(ROOT);backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old_path.read_bytes())
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаляется только побайтово сверенный заменённый ресурс внутри его исходной папки.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==backup.read_bytes()==source[0x6F0B:0x6F2B];old_path.unlink()
    report=dict(passed=True,physical_records=2,typed_bytes=10,structure='FRenderProjectedPoint',original_bytes_preserved=True,old_address_aliases_removed=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipPointsDataClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
