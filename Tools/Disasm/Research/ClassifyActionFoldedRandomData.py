"""Точечное выделение девяти доказанных байтов из 73-байтового физического блока."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionFoldedRandomData as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionFoldedRandomVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=[read(name) for name in ('SourceMap','Symbols','Inventory')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x8BBF)
    assert (old['length'],old['kind'])==(73,'unclassified')
    previous=ROOT/old['path'];before_previous=previous.read_bytes()
    assert before_previous==source[0x8BBF:0x8C08]
    tables={t[2]:t for t in facts.TABLES}
    pieces=((0x8BBF,0x8BDE,'Source/Resources/17_ACTION/FoldRandomBefore.bin'),
        (0x8BDE,0x8BE1,tables[0x8BDE][1]),
        (0x8BE1,0x8BEA,'Source/Resources/17_ACTION/FoldRandomBetween0And2.bin'),
        (0x8BEA,0x8BED,tables[0x8BEA][1]),
        (0x8BED,0x8C02,'Source/Resources/17_ACTION/FoldRandomBetween2And1.bin'),
        (0x8C02,0x8C05,tables[0x8C02][1]),
        (0x8C05,0x8C08,'Source/Resources/17_ACTION/FoldRandomAfter.bin'))
    pending={};ranges=[]
    for start,end,path in pieces:
        typed=start in tables
        if typed:
            text,bindings=facts.render(source,tables[start])
            assert facts.parse(text,tables[start])==(source[start:end],bindings)
            assert not set(bindings)&set(symbols);symbols.update(bindings)
            pending[ROOT/path]=text.encode('utf-8')
        else:pending[ROOT/path]=source[start:end]
        ranges.append(dict(slot=17,offset=start,length=end-start,kind='typed_data' if typed else 'unclassified',
            path=path,origin=start+0x6000 if typed else None,sha256=hashlib.sha256(source[start:end]).hexdigest()))
    at=source_map.index(old);source_map[at:at+1]=ranges
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"';assert text.count(needle)==1
    lines=[]
    for start,end,relative in pieces:
        lines+=['                assert $ == #'+format(start,'04X')]
        if start in tables:
            lines+=['                disp #'+format(start+0x6000,'04X'),
                '                include "../Action/Data/'+relative.rsplit('/',1)[-1]+'"','                ent']
        else:lines+=['                ; Соседние исходные байты, назначение не установлено',
                '                incbin "../Resources/17_ACTION/'+relative.rsplit('/',1)[-1]+'"']
    pending[path]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    assert 'struct FFoldedRandomState' not in text and text.count('                endif')==1
    block='\n                ; Физическая запись трёхбайтового состояния генератора ACTION\n                struct FFoldedRandomState\n'
    block+='LowWord'.ljust(16)+'dw #0000'.ljust(64)+'; слово смешивания и возвращаемого 16-битного результата\n'
    block+='FoldByte'.ljust(16)+'db #00'.ljust(64)+'; байт свёртки переносов, числовая величина modulo 256\n'
    block+='                ends\n                assert FFoldedRandomState == 3\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    anchor='    token_text, token_records = render_token_tables(language, names)';assert text.count(anchor)==1
    hook='''    # Три физических трёхбайтовых состояния генератора ACTION, девять исходных байтов.
    if "struct FFoldedRandomState" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionFoldedRandomData import TABLES as FOLDED_STATES, render as render_folded_state
        for table in FOLDED_STATES:
            text, bindings = render_folded_state(data_by_slot[17], table)
            write(table[1], text)
            symbols.update(bindings)
            special[17, table[2]] = (table[3], table[1], table[2]+0x6000)
'''
    pending[path]=text.replace(anchor,hook+anchor).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    anchor='    # Проверка двух физических слов состояния генератора ACTION.';assert text.count(anchor)==1
    hook='''    # Проверка трёх физических записей LowWord и FoldByte, не адресных псевдонимов.
    from ActionFoldedRandomData import TABLES as FOLDED_STATES, parse as parse_folded_state
    folded_random_records = 0
    for table in FOLDED_STATES:
        entries = [item for item in source_map if item['path']==table[1]]
        if not entries:
            continue
        assert len(entries)==1
        item=entries[0]
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,table[2],3,table[2]+0x6000)
        raw,bindings=parse_folded_state((ROOT/table[1]).read_text('utf-8'),table)
        assert raw==sources[17][table[2]:table[3]]
        assert all(symbols.get(key.upper())==value for key,value in bindings.items())
        assert symbols['FFOLDEDRANDOMSTATE']==3
        assert symbols['FFOLDEDRANDOMSTATE.LOWWORD']==0 and symbols['FFOLDEDRANDOMSTATE.FOLDBYTE']==2
        folded_random_records+=1

'''
    text=text.replace(anchor,hook+anchor)
    anchor="    report['word_random_records'] = word_random_records";assert text.count(anchor)==1
    pending[path]=text.replace(anchor,anchor+"\n    report['folded_random_records'] = folded_random_records").encode('utf-8')
    for relative in ('Docs/DataFormats.md','Tools/Disasm/Research/GenerateDocs.py'):
        path=ROOT/relative;text=path.read_text('utf-8')
        row='| FFoldedRandomState | #03 | три физических LowWord и FoldByte, см. [ActionFoldedRandom](ActionFoldedRandom.md) |'
        if relative=='Docs/DataFormats.md':
            assert 'FFoldedRandomState' not in text
            extra='\nТри физических `FFoldedRandomState` по три байта, LowWord по смещениям 0..1 и FoldByte по смещению 2, размещены в [Stream0](../Source/Action/Data/FoldRandomStream0.asm), [Stream1](../Source/Action/Data/FoldRandomStream1.asm) и [Stream2](../Source/Action/Data/FoldRandomStream2.asm). Исходные девять байтов EBDE, EC02 и EBEA сохранены, FoldByte является числовой величиной, не набором флагов. Формула и границы проверки приведены в [ActionFoldedRandom](ActionFoldedRandom.md).\n'
            pending[path]=(text+extra).encode('utf-8')
            continue
        lines=text.splitlines();indices=[i for i,line in enumerate(lines) if '| FWordRandomState |' in line]
        assert len(indices)==1 and '| FFoldedRandomState |' not in text
        at=indices[0]+1;lines.insert(at,('               "'+row+'",') if relative.endswith('.py') else row)
        pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionFoldedRandomData'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionFoldedRandomData'
    assert not candidate.exists() and not history.exists()
    plan=[(path,path.read_bytes() if path.exists() else None,after) for path,after in pending.items()]
    # Создание отдельного кандидата и точных исходных контрольных копий.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=history/previous.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before_previous)
    # Проверка отсутствия конкурирующих правок перед заменой.
    for path,before,_ in plan:assert (path.read_bytes() if path.exists() else None)==before
    for path,_,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённого ресурса после побайтовой проверки и сохранения копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==before_previous==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,typed_bytes=9,physical_records=3,structure='FFoldedRandomState',
        offsets=[t[2] for t in facts.TABLES],neighboring_unknown_bytes_preserved=64,
        full_original_block_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionFoldedRandomDataClassification.json').write_bytes(encode(report))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
