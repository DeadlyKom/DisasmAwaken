"""Публикация распознанного графического файла, исходные пиксели и секторный хвост не меняются."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
import Scene1PixelPairs as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
import VerifySources


def main():
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('Scene1PixelPairsVerification');assert proof['passed'] and proof['all_bytes_roundtrip']
    source_map,inventory=read('SourceMap'),read('Inventory')
    rows=[r for r in source_map if r['slot']==facts.SLOT];assert len(rows)==1
    old=rows[0];assert old['kind']=='unclassified' and old['offset']==0 and old['length']==18688
    old_path=ROOT/old['path'];original=old_path.read_bytes()
    data=(ROOT/'Tools/Disasm/Extracted/Active/30_scene1po.s.bin').read_bytes()
    assert original[:facts.LOGICAL_BYTES]==data and len(data)==facts.LOGICAL_BYTES
    assert facts.pack(facts.unpack(data))==data and hashlib.sha256(data).hexdigest()==proof['sha256']
    assert not any(r.get('target_path')==old['path'] for r in read('ModifiedCode'))
    pending={ROOT/facts.PATH:data,ROOT/facts.TAIL_PATH:original[len(data):]}
    assert not any(p.exists() for p in pending)
    replacements=[]
    for start,end,path,kind in ((0,len(data),facts.PATH,'binary_resource'),(len(data),len(original),facts.TAIL_PATH,'unclassified')):
        row=dict(slot=facts.SLOT,offset=start,length=end-start,path=path,kind=kind,origin=None,
                 sha256=hashlib.sha256(original[start:end]).hexdigest())
        if kind=='binary_resource':row['format']=facts.FORMAT
        replacements.append(row)
    index=source_map.index(old);source_map[index:index+1]=replacements
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(r['length'] for r in source_map if r['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending[reports/'SourceMap.json']=encode(source_map);pending[reports/'Inventory.json']=encode(inventory)
    p=ROOT/'Source/Files/30_scene1po.inc';text=p.read_text('utf-8')
    needle='                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/30_scene1po/Unclassified000.bin"'
    assert text.count(needle)==1
    replacement=('                ; Документация [графический файл и пределы интерпретации](../../Docs/Scene1PixelPairs.md)\n'
                 '                incbin "../Resources/30_scene1po/PixelPairs.bin"\n'
                 '                assert $ == #48F4\n'
                 '                ; Unknown, двенадцать байтов хвоста секторов сохраняются буквально\n'
                 '                incbin "../Resources/30_scene1po/SectorTail.bin"')
    pending[p]=text.replace(needle,replacement).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8')
    needle='    binary_resources[7, 0x2900]'
    assert text.count(needle)==1
    hook=('    # Графический scene1po сохраняется без пересчёта пикселей, геометрия остаётся исследовательской.\n'
          '    from Scene1PixelPairs import SLOT as SCENE1_SLOT, LOGICAL_BYTES as SCENE1_BYTES, PATH as SCENE1_PATH, TAIL_PATH as SCENE1_TAIL_PATH, FORMAT as SCENE1_FORMAT\n'
          '    binary_resources[SCENE1_SLOT,0]=(SCENE1_BYTES,SCENE1_PATH,SCENE1_FORMAT)\n')
    text=text.replace(needle,hook+needle)
    needle='                path = ROOT / binary_path'
    assert text.count(needle)==1
    text=text.replace(needle,'                if slot==SCENE1_SLOT and begin==SCENE1_BYTES:binary_path=SCENE1_TAIL_PATH\n'+needle)
    pending[p]=text.encode('utf-8')
    p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка исходных графических байтов scene1po, загрузчик и палитра этим не доказываются.
    import Scene1PixelPairs as scene1
    scene1_rows=[r for r in source_map if r['slot']==scene1.SLOT]
    assert [(r['offset'],r['length'],r['kind'],r['path']) for r in scene1_rows]==[
        (0,scene1.LOGICAL_BYTES,'binary_resource',scene1.PATH),
        (scene1.LOGICAL_BYTES,12,'unclassified',scene1.TAIL_PATH)]
    scene1_data=(ROOT/scene1.PATH).read_bytes()
    assert scene1_data==sources[scene1.SLOT][:scene1.LOGICAL_BYTES]
    assert scene1.pack(scene1.unpack(scene1_data))==scene1_data

'''
    pending[p]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/Scene1PixelPairs'
    history=ROOT/'Tools/Disasm/Research/History/BeforeScene1PixelPairs'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    q=history/old_path.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(original)
    for p,before,after in plan:
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=p.parent,prefix='scene-resource-',suffix='.tmp',delete=False) as out:
                temporary=out.name;out.write(after)
            os.replace(temporary,p)
        else:p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
    assert old_path.read_bytes()==original==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,logical_bytes_classified_as_graphic_resource=len(data),unclassified_sector_tail_bytes=12,
        original_bytes_and_physical_layout_preserved=True,runtime_loader_proved=False,
        geometry_from_runtime_metadata=False,runtime_plane_combination_proved=False,
        python_needed_for_ordinary_build=False,assembly_executed=False,native_execution=False)
    (reports/'Scene1PixelPairsClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
