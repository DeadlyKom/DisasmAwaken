"""Публикация четырёх реальных STRUCT, кандидата и истории, сборка не запускается."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionClipProductsData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionClipProductsVerification')['passed'] and read('ActionClipProductsClassification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    old=next(x for x in source_map if x['slot']==17 and x['offset']<=0x6F2B<x['offset']+x['length'])
    assert (old['offset'],old['length'],old['kind'])==(0x6F0B,511,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x6F0B:0x710A]
    text,labels=facts.render(source);assert facts.parse(text)==(source[0x6F2B:0x6F3B],labels)
    assert not set(labels)&set(symbols);symbols.update(labels)
    pieces=((0x6F0B,0x6F2B,'Source/Resources/17_ACTION/Unclassified027_BeforeProducts.bin',False),
        (0x6F2B,0x6F3B,facts.PATH,True),(0x6F3B,0x710A,'Source/Resources/17_ACTION/Unclassified027_AfterProducts.bin',False))
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
        if typed:lines+=['                disp #CF2B','                include "../Action/Data/ClipProducts.asm"','                ent']
        else:lines+=['                incbin "../Resources/17_ACTION/'+path.rsplit('/',1)[-1]+'"']
    pending[p]=t.replace(needle,'\n'.join(lines)).encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';t=p.read_text('utf-8');needle='    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.';assert t.count(needle)==1
    hook='''    # Проверка реальных четырёх FClipProduct, всех полей и физических исходных байтов.
    from ActionClipProductsData import PATH as CLIP_PRODUCTS_PATH, parse as parse_clip_products
    clip_raw,clip_labels=parse_clip_products((ROOT/CLIP_PRODUCTS_PATH).read_text('utf-8'))
    assert clip_raw==sources[17][0x6F2B:0x6F3B]
    assert all(symbols.get(k.upper())==v for k,v in clip_labels.items())
    assert symbols['FCLIPPRODUCT']==4 and symbols['FCLIPPRODUCT.LOWWORD']==0 and symbols['FCLIPPRODUCT.HIGHWORD']==2
    clip_items=[x for x in source_map if x['path']==CLIP_PRODUCTS_PATH]
    assert len(clip_items)==1 and (clip_items[0]['offset'],clip_items[0]['length'],clip_items[0]['origin'])==(0x6F2B,16,0xCF2B)

'''
    pending[p]=t.replace(needle,hook+needle).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';t=p.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert t.count(needle)==1
    hook='''    # Реальные ячейки произведений ACTION внутри невыбираемых областей таблицы.
    from ActionClipProductsData import PATH as CLIP_PRODUCTS_PATH, render as render_clip_products
    text,bindings=render_clip_products(data_by_slot[17])
    write(CLIP_PRODUCTS_PATH,text)
    symbols.update(bindings)
    special[17,0x6F2B]=(0x6F3B,CLIP_PRODUCTS_PATH,0xCF2B)
'''
    pending[p]=t.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionClipProductsData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionClipProductsData'
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
    assert old_path.read_bytes()==backup.read_bytes()==source[0x6F0B:0x710A];old_path.unlink()
    report=dict(passed=True,typed_bytes=16,physical_records=4,structure='FClipProduct',original_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipProductsDataClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
