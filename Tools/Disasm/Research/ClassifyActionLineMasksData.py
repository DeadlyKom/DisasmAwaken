"""Публикация шестнадцати физических масок, кандидата и истории, сборка не запускается."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionLineMasksData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionLineRasterVerification')['passed'] and read('ActionLineRasterClassification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    old=next(x for x in source_map if x['slot']==17 and x['offset']<=0x8010<x['offset']+x['length'])
    assert (old['offset'],old['length'],old['kind'])==(0x8009,23,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x8009:0x8020]
    text,labels=facts.render(source);assert facts.parse(text)==(source[0x8010:0x8020],labels)
    assert not set(labels)&set(symbols);symbols.update(labels)
    pieces=((0x8009,0x8010,'Source/Resources/17_ACTION/Unclassified028_BeforeLineMasks.bin',False),(0x8010,0x8020,facts.PATH,True))
    pending={ROOT/facts.PATH:text.encode('utf-8')};ranges=[]
    for start,end,path,typed in pieces:
        if not typed:pending[ROOT/path]=source[start:end]
        ranges.append(dict(slot=17,offset=start,length=end-start,kind='typed_data' if typed else 'unclassified',
            path=path,origin=start+0x6000 if typed else None,sha256=hashlib.sha256(source[start:end]).hexdigest()))
    index=source_map.index(old);source_map[index:index+1]=ranges
    inventory['ranges_by_kind']=dict(Counter(x['kind'] for x in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(x['length'] for x in source_map if x['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    p=ROOT/'Source/Files/17_ACTION.inc';t=p.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert t.count(needle)==1
    lines=[]
    for start,end,path,typed in pieces:
        lines+=['                assert $ == #'+format(start,'04X')]
        if typed:lines+=['                disp #E010','                include "../Action/Data/LineMasks.asm"','                ent']
        else:lines+=['                incbin "../Resources/17_ACTION/'+path.rsplit('/',1)[-1]+'"']
    pending[p]=t.replace(needle,'\n'.join(lines)).encode('utf-8')
    p=ROOT/'Includes/Structs/Include.inc';current=p.read_text('utf-8');assert 'struct FLinePixelMask' not in current
    pending[p]=current.replace('                endif',facts.structure_text()+'\n                endif').encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.';assert t.count(needle)==1
    hook='''    # Проверка шестнадцати FLinePixelMask, всех полей и физических исходных байтов.
    from ActionLineMasksData import PATH as LINE_MASKS_PATH, parse as parse_line_masks
    clip_raw,clip_labels=parse_line_masks((ROOT/LINE_MASKS_PATH).read_text('utf-8'))
    assert clip_raw==sources[17][0x8010:0x8020]
    assert all(symbols.get(k.upper())==v for k,v in clip_labels.items())
    assert symbols['FLINEPIXELMASK']==1 and symbols['FLINEPIXELMASK.MASK']==0
    clip_items=[x for x in source_map if x['path']==LINE_MASKS_PATH]
    assert len(clip_items)==1 and (clip_items[0]['offset'],clip_items[0]['length'],clip_items[0]['origin'])==(0x8010,16,0xE010)

'''
    pending[p]=t.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';t=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert t.count(needle)==1
    hook='''    # Реальные пиксельные маски ACTION внутри невыбираемых областей таблицы.
    from ActionLineMasksData import PATH as LINE_MASKS_PATH, render as render_line_masks
    text,bindings=render_line_masks(data_by_slot[17])
    write(LINE_MASKS_PATH,text)
    symbols.update(bindings)
    special[17,0x8010]=(0x8020,LINE_MASKS_PATH,0xE010)
'''
    pending[p]=t.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionLineMasksData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionLineMasksData'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    # Подготовка отдельного кандидата и проверка отсутствия пересекающихся изменений.
    for p,before,data in plan:
        c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
    for p,before,data in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,data in plan:
        if before is not None:
            h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(before)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    backup=history/old_path.relative_to(ROOT);backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old_path.read_bytes())
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённого ресурса после сохранения и сверки его точных байтов.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==backup.read_bytes()==source[0x8009:0x8020];old_path.unlink()
    report=dict(passed=True,typed_bytes=16,physical_records=16,structure='FLinePixelMask',original_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionLineMasksDataClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
