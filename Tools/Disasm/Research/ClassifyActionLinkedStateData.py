"""Публикация 13 доказанных физических байтов и замена адресных EQU реальными экземплярами STRUCT."""
from collections import Counter
import contextlib,hashlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionLinkedStateData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionOverlayPairVerification')['passed'] and read('ActionSpawnWindowVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();sm,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    pending={};removed=[];include_path=ROOT/'Source/Files/17_ACTION.inc';include=include_path.read_text('utf-8');new_symbols=0
    for table in facts.TABLES:
        module,path,start,end,structure,fields,names=table
        old=next(p for p in sm if p['slot']==17 and p['offset']==start);assert old['kind']=='unclassified' and old['length']==end-start
        old_path=ROOT/old['path'];assert old_path.read_bytes()==source[start:end];removed.append((old_path,source[start:end]))
        text,labels=facts.render(source,table);assert facts.parse(text,table)==(source[start:end],labels)
        assert not set(labels)&set(symbols);symbols.update(labels);new_symbols+=len(labels);pending[ROOT/path]=text.encode('utf-8')
        old.update(kind='typed_data',path=path,origin=start+0x6000)
        needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert include.count(needle)==1
        replacement='                disp #'+format(start+0x6000,'04X')+'\n                include "../Action/Data/'+path.rsplit('/',1)[-1]+'"\n                ent'
        include=include.replace(needle,replacement)
    pending[include_path]=include.encode('utf-8')
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm));inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FOverlayLine' not in text and 'struct FClassSpawnByte' not in text
    pending[path]=text.replace('                endif',facts.structures()+'\n                endif').encode('utf-8')
    # Удаление только двух адресных модулей с единственной привязкой, реальная память остаётся на прежнем месте.
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8')
    for module in ('ActionOverlayPairState','ActionSpawnWindowState'):
        start=text.index('                module '+module+'\n');end=text.index('                endmodule',start)+len('                endmodule\n')
        block=text[start:end];assert sum('equ #' in line for line in block.splitlines())==1;text=text[:start]+text[end:]
    pending[path]=text.encode('utf-8')
    renames=(('@ActionOverlayPairState.LineStream','@ActionOverlayLineData.Line'),('@ActionSpawnWindowState.ClassValues','@ActionClassSpawnValues.Class0.Value'))
    for relative in ('Source/Action/ToggleTargetOverlay.asm','Source/Action/CheckClass17SpawnWindow.asm',
                     'Tools/Disasm/Research/ActionOverlayPairFacts.py','Tools/Disasm/Research/ActionSpawnWindowFacts.py'):
        path=ROOT/relative;text=path.read_text('utf-8')
        for before,after in renames:text=text.replace(before,after)
        pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка двух физических точек, их вложенных координат и кода, а не только адресных EQU.';assert text.count(needle)==1
    hook='''    # Проверка физических STRUCT двух малых ресурсов связанных состояний.
    from ActionLinkedStateData import TABLES as LINKED_STATE_TABLES, parse as parse_linked_state_data
    for table in LINKED_STATE_TABLES:
        _,path,start,end,_,_,_=table
        raw,labels=parse_linked_state_data((ROOT/path).read_text('utf-8'),table)
        assert raw==sources[17][start:end]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        rows=[p for p in source_map if p['path']==path]
        assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(start,end-start,start+0x6000)
    assert symbols['FOVERLAYLINE']==4 and symbols['FCLASSSPAWNBYTE']==1

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические поток XOR-линии и классовые байты, ручные экземпляры сохраняются.
    from ActionLinkedStateData import TABLES as LINKED_STATE_TABLES, render as render_linked_state_data
    for table in LINKED_STATE_TABLES:
        text,labels=render_linked_state_data(data_by_slot[17],table)
        write(table[1],text);symbols.update(labels)
        special[17,table[2]]=(table[3],table[1],table[2]+0x6000)

'''
    # Существующий экспорт использует индивидуальные типизированные привязки, механизм проверяется перед записью.
    assert 'data_by_slot' in text and 'special[17,' in text
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    for relative,extra in (('Docs/ActionOverlayPair.md','\nИсходные четыре байта оформлены физическим [экземпляром FOverlayLine](../Source/Action/Data/OverlayLine.asm). Адресный EQU заменён ссылкой на этот экземпляр, поля и конец потока проверяются отдельно.\n'),
                           ('Docs/ActionSpawnWindow.md','\nДевять исходных значений оформлены физическими [FClassSpawnByte Class0..Class8](../Source/Action/Data/ClassSpawnValues.asm). Полное индексирование за последним элементом не ограничено и по-прежнему читает следующие исходные байты.\n')):
        path=ROOT/relative;pending[path]=(path.read_text('utf-8')+extra).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionLinkedStateData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionLinkedStateData'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,a) for p,a in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before in removed:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='linked-data-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    for path,before in removed:
        assert path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
        assert path.read_bytes()==before==(history/path.relative_to(ROOT)).read_bytes();path.unlink()
    result=dict(passed=True,typed_bytes=13,physical_records=10,new_physical_symbols=new_symbols,original_bytes_preserved=True,address_alias_modules_removed=2,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedStateDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
