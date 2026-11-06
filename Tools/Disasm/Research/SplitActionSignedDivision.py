"""Разделение двух уже существующих входов C88C и C941 без экспорта ручных исходников."""
from pathlib import Path
import json,hashlib,contextlib,io,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionSignedDivisionVerification')['passed']
    functions,source_map,symbols,inventory,flow,mutations=[read(n) for n in ('Functions','SourceMap','Symbols','Inventory','ControlFlow','ModifiedCode')]
    old=next(f for f in functions if f['region']=='Action' and f['address']==0xC88C)
    assert old['end_offset']==0x699B
    path=ROOT/old['path'];text=path.read_text('utf-8')
    needle='                LD A, #01\n                LD (#CF03), A'
    assert text.count(needle)==1
    cut=text.index(needle);header=text[:text.index('Entry:')]
    first=text[:cut].rstrip()+'\n\n                endmodule\n                endmodule\n'
    first=first.replace('#688C..#699A','#688C..#6940')
    first=first.replace('; Документация [Action](../../Docs/FunctionDetails/Action.md)',
        '; Документация [делитель и проверка](../../Docs/ActionSignedDivision.md)')
    tail=header.replace('module UnknownC88C','module UnknownC941').replace('#688C..#699A','#6941..#699A')
    tail+=text[cut:].replace('                LD A, #01\n','Entry:          LD A, #01\n',1)
    tail=tail.replace('Action.UnknownC88C.PointC974','Action.UnknownC941.PointC974')
    pending={path:first.encode('utf-8'),ROOT/'Source/Action/UnknownC941.asm':tail.encode('utf-8')}
    # Перенос только меток второго входа, индекс и staged-версии не затрагиваются.
    for key,value in list(symbols.items()):
        if key.startswith('Action.UnknownC88C.') and value>=0xC941:
            symbols[key.replace('UnknownC88C','UnknownC941')]=symbols.pop(key)
    symbols['Action.UnknownC941.Entry']=0xC941
    suffix=dict(old,name='UnknownC941',address=0xC941,offset=0x6941,path='Source/Action/UnknownC941.asm',
        description='Unknown, полный договор диспетчера отсечения ещё не установлен')
    index=functions.index(old);functions.insert(index+1,suffix);old['end_offset']=0x6941
    original=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    span=next(s for s in source_map if s['path']==old['path']);index=source_map.index(span)
    source_map[index:index+1]=[dict(span,offset=f['offset'],length=f['end_offset']-f['offset'],path=f['path'],origin=f['address'],
        sha256=hashlib.sha256(original[f['offset']:f['end_offset']]).hexdigest()) for f in (old,suffix)]
    region=next(r for r in flow if r['name']=='Action');region['roots']=sorted(set(region['roots'])|{0xC941})
    for m in mutations:
        if m['path']==old['path'] and m['writer']>=0xC941:m['path']=suffix['path']
    inventory['fragments']=len(functions);inventory['unknown']=sum(f['semantic_status']=='unknown' for f in functions)
    p=ROOT/'Source/Files/17_ACTION.inc';t=p.read_text('utf-8');needle='                include "../Action/UnknownC88C.asm"';assert t.count(needle)==1
    pending[p]=t.replace(needle,needle+'\n                ent\n                assert $ == #6941\n                disp #C941\n                include "../Action/UnknownC941.asm"').encode('utf-8')
    for directory,pattern in (('Source','*.asm'),('Docs','*.md')):
        for p in (ROOT/directory).rglob(pattern):
            if p==path:continue
            t=p.read_text('utf-8');after=t.replace('Action.UnknownC88C.PointC974','Action.UnknownC941.PointC974')
            if t!=after:pending[p]=after.encode('utf-8')
    p=ROOT/'Docs/Functions.md';t=p.read_text('utf-8');needle='| #C99B |';assert t.count(needle)==1
    row='| #C941 | [Action.UnknownC941](../Source/Action/UnknownC941.asm) | Unknown, договор диспетчера отсечения не установлен |\n'
    pending[p]=t.replace(needle,row+needle).encode('utf-8')
    p=ROOT/'Docs/FunctionDetails/Action.md';t=p.read_text('utf-8');needle='## BuildRenderCoefficients\n';assert t.count(needle)==1
    pending[p]=t.replace(needle,'## UnknownC941\n\n[Action.UnknownC941](../../Source/Action/UnknownC941.asm)\n\nUnknown, полный договор диспетчера отсечения не установлен.\n\n'+needle).encode('utf-8')
    for name,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('ControlFlow',flow),('ModifiedCode',mutations)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionDivisionSplit';history=ROOT/'Tools/Disasm/Research/History/BeforeActionDivisionSplit'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    # Подготовка кандидата, проверка отсутствия новых чужих изменений и сохранение точной истории.
    for p,before,data in plan:
        c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
    for p,before,data in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,data in plan:
        if before is not None:
            h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(before)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    report=dict(passed=True,original_bytes_preserved=True,instructions_changed=0,division_bytes=181,dispatcher_bytes=90,
        semantic_status_of_both_fragments='unknown_pending_separate_publication',assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionDivisionSplitClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
