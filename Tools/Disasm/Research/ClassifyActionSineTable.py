"""Типизация 256 байтов синусоиды без изменения окружающей исходной области ACTION."""
from pathlib import Path
import collections
import contextlib
import hashlib
import io
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
import ActionSineTable as facts


def main():
    def read(stem):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    raw=facts.validate(source)
    entry=next(e for e in read_disk()['entries'] if e['slot']==17)
    assert entry['parameter']==0x6000
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==17 and i['offset']<=0x3900<i['offset']+i['length'])
    assert (item['offset'],item['length'],item['kind'])==(0x21CC,0x2661,'unclassified')
    previous=ROOT/item['path']
    original=previous.read_bytes()
    assert original==source[0x21CC:0x482D]
    text,labels=facts.render(source)
    assert facts.parse(text)==(raw,labels)
    assert not any(name in symbols for name in labels)
    symbols.update(labels)
    prefix='Source/Resources/17_ACTION/Unclassified020_Prefix.bin'
    suffix='Source/Resources/17_ACTION/Unclassified020_Suffix.bin'
    pieces=[]
    for start,end,kind,path,origin in ((0x21CC,0x3900,'unclassified',prefix,None),
        (0x3900,0x3A00,'typed_data',facts.TABLE[1],0x9900),(0x3A00,0x482D,'unclassified',suffix,None)):
        pieces.append(dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
            sha256=hashlib.sha256(source[start:end]).hexdigest()))
    index=source_map.index(item)
    source_map[index:index+1]=pieces
    inventory['ranges_by_kind']=dict(collections.Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    assert sum(inventory['physical_bytes_by_kind'].values())==479744
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/prefix:source[0x21CC:0x3900],ROOT/suffix:source[0x3A00:0x482D]}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc'
    text=path.read_text('utf-8')
    assert 'struct FFixedSineValue' not in text
    block=('\n                ; Физический знаковый отсчёт синусоиды ACTION\n'
        '                struct FFixedSineValue\n'
        'Value           db #00                                                          ; синус в дополнительном коде, масштаб 128\n'
        '                ends\n                assert FFixedSineValue == 1\n')
    pending[path]=text.replace('                endif',block+'\n                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc'
    text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/Unclassified020.bin"'
    assert text.count(needle)==1
    replacement=('                incbin "../Resources/17_ACTION/Unclassified020_Prefix.bin"\n'
        '                assert $ == #3900\n                disp #9900\n'
        '                include "../Action/Data/SineTable.asm"\n                ent\n'
        '                assert $ == #3A00\n'
        '                ; Unknown, исходные байты после синусоиды ACTION\n'
        '                incbin "../Resources/17_ACTION/Unclassified020_Suffix.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py'
    text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook=('    # Исходные 256 отсчётов синуса формируются из байтов, не из новой формулы.\n'
        '    if "struct FFixedSineValue" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ActionSineTable import TABLE as ACTION_SINE_TABLE, render as render_action_sine\n'
        '        text, bindings = render_action_sine(data_by_slot[17])\n'
        '        write(ACTION_SINE_TABLE[1], text)\n        symbols.update(bindings)\n'
        '        special[17, 0x3900] = (0x3A00, ACTION_SINE_TABLE[1], 0x9900)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionSineTable'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionSineTable'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,typed_bytes=256,physical_records=256,logical_file_offset=0x3900,runtime_address=0x9900,
        signed_minimum=-127,signed_maximum=127,scale=128,half_period_antisymmetry=True,
        formula_matches_all_original_bytes=True,formula_used_to_regenerate_build_data=False,
        physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionSineTableClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


def read_disk():
    return json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))


if __name__=='__main__':
    main()
