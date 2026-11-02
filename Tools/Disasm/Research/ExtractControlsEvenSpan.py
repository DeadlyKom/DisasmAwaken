"""Выделение 24 исполненных байтов динамического заполнителя, без сборки."""
from collections import Counter
import contextlib
import io
import json
import hashlib
import sys
from ClassifyControlsTextDisplay import ROOT
from InspectZ80 import decoder
from CheckControlsTextQueue import base_memory
from VerifySources import main as verify


def main():
    def read(name):
        return json.loads((ROOT / ('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    # Проверка исходной разметки и доказанной достижимости всех динамических входов.
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read('ControlsEvenSpanVerification')
    assert proof['passed'] and len(proof['dynamic_targets']) == 15
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ControlsEvenSpanCode'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsEvenSpanCode'
    assert not candidate.exists() and not history.exists()
    flow,functions,symbols,source_map = (read(n) for n in ('ControlFlow','Functions','Symbols','SourceMap'))
    region = next(r for r in flow if r['name'] == 'Controls')
    decoded = list(decoder(base_memory()).disassemble(0xCEB7,0xCECF,'h'))
    assert len(decoded) == 24 and all(i.operation in ('DEC L','LD (HL),A') for i in decoded)
    assert not any(0xCEB7 <= i['address'] < 0xCECF for i in region['instructions'])
    instructions = [dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=22,offset=i.address-0xC000) for i in decoded]
    region['instructions'] = sorted(region['instructions']+instructions,key=lambda i:(i['slot'],i['offset']))
    region['roots'] = sorted(set(region['roots'])|{0xCEB7})
    region['instruction_count'] += 24
    region['code_bytes'] += 24
    region['classified_fraction'] = region['code_bytes']/region['total_bytes']
    function = dict(region='Controls',name='UnknownCEB7',address=0xCEB7,slot=22,offset=0xEB7,end_offset=0xECF,
        description='Unknown, назначение этого фрагмента ещё не установлено',semantic_status='unknown',path='Source/Controls/UnknownCEB7.asm')
    index = next(n for n,f in enumerate(functions) if f['region'] == 'Controls' and f['address'] == 0xCEA4)
    functions.insert(index+1,function)
    assert 'Controls.UnknownCEB7.Entry' not in symbols
    symbols['Controls.UnknownCEB7.Entry'] = 0xCEB7
    lines = ['                module Controls','                module UnknownCEB7',
        '                ; Документация [динамические входы](../../Docs/ControlsEvenSpan.md)']
    for index,i in enumerate(decoded):
        lines.append(('Entry:'.ljust(16) if index == 0 else ' '*16)+i.operation.replace(',',', '))
    lines += ['                ; JP @Controls.UnknownCECF.Entry, продолжение в UnknownCECF.asm','                endmodule','                endmodule']
    pending = {ROOT/function['path']:('\n'.join(lines)+'\n').encode('utf-8')}
    item = next(i for i in source_map if i['slot'] == 22 and i['offset'] == 0xEB5)
    assert item['kind'] == 'unclassified' and item['length'] == 26
    previous = ROOT/item['path']
    original = previous.read_bytes()
    assert original == bytes(base_memory()[0xCEB5:0xCECF])
    prefix = 'Source/Resources/22_CONTROL0/Unclassified002_Prefix.bin'
    item.update(length=2,path=prefix,sha256=hashlib.sha256(original[:2]).hexdigest())
    source_map.insert(source_map.index(item)+1,dict(slot=22,offset=0xEB7,length=24,kind='code',origin=0xCEB7,path=function['path'],sha256=hashlib.sha256(original[2:]).hexdigest()))
    pending[ROOT/prefix] = original[:2]
    inventory = read('Inventory')
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
        unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+24)
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('ControlFlow',flow),('Functions',functions),('Symbols',symbols),('SourceMap',source_map),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')] = encode(value)
    path = ROOT/'Source/Files/22_CONTROL0.inc'
    text = path.read_text('utf-8')
    needle = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/22_CONTROL0/Unclassified002.bin"'
    assert text.count(needle) == 1
    replacement = ('                ; Два байта CEB5..CEB6 не достигаются при A=0..15, назначение отдельно не установлено\n'
        '                incbin "../Resources/22_CONTROL0/Unclassified002_Prefix.bin"\n'
        '                assert $ == #0EB7\n                disp #CEB7\n                include "../Controls/UnknownCEB7.asm"\n                ent')
    pending[path] = text.replace(needle,replacement).encode('utf-8')
    path = ROOT/'Docs/Functions.md'
    text = path.read_text('utf-8')
    needle = '| #CECF | [Controls.UnknownCECF]'
    assert text.count(needle) == 1
    row = '| #CEB7 | [Controls.UnknownCEB7](../Source/Controls/UnknownCEB7.asm) | Unknown, назначение этого фрагмента ещё не установлено |\n'
    text = text.replace(needle,row+needle)
    text = text.replace('| Controls | 68 |','| Controls | 69 |')
    pending[path] = text.encode('utf-8')
    path = ROOT/'Docs/FunctionDetails/Controls.md'
    text = path.read_text('utf-8')
    block = ('## UnknownCEB7\n\n[Controls.UnknownCEB7](../../Source/Controls/UnknownCEB7.asm)\n\n'
        'Unknown, назначение этого фрагмента ещё не установлено.\n\n'
        'Вход `#CEB7`, запись 22, смещения `#0EB7..#0ECE`.\n\n')
    assert '## UnknownCEB7\n' not in text
    pending[path] = text.replace('## UnknownCECF\n',block+'## UnknownCECF\n').encode('utf-8')
    # Создание отдельного кандидата и сохранение прежних версий перед точечной заменой.
    plan = [(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target = candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target = history/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
    assert previous.read_bytes() == original == (history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report = dict(passed=True,extracted_code_bytes=24,new_instructions=24,registered_entry='CEB7',
        original_unused_prefix_preserved=2,dynamic_targets_proved=15,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsEvenSpanCodeClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    if '--complete' in sys.argv:
        # Завершение уже применённого разделения, контрольные суммы меняются только у двух точных диапазонов.
        previous = ROOT/'Source/Resources/22_CONTROL0/Unclassified002.bin'
        history = ROOT/'Tools/Disasm/Research/History/BeforeControlsEvenSpanCode'
        original = previous.read_bytes()
        assert original == (history/previous.relative_to(ROOT)).read_bytes() == bytes(base_memory()[0xCEB5:0xCECF])
        path = ROOT/'Tools/Disasm/Reports/SourceMap.json'
        values = json.loads(path.read_text('utf-8'))
        for offset,length,start,kind in ((0xEB5,2,0,'unclassified'),(0xEB7,24,2,'code')):
            item = next(i for i in values if i['slot']==22 and i['offset']==offset)
            assert item['length']==length and item['kind']==kind
            item['sha256'] = hashlib.sha256(original[start:start+length]).hexdigest()
        path.write_text(json.dumps(values,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            verify()
        assert previous.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
        assert previous.read_bytes()==original
        previous.unlink()
        report = dict(passed=True,extracted_code_bytes=24,new_instructions=24,registered_entry='CEB7',
            original_unused_prefix_preserved=2,dynamic_targets_proved=15,physical_bytes_preserved=True,assembly_executed=False)
        (ROOT/'Tools/Disasm/Reports/ControlsEvenSpanCodeClassification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2))
    else:
        main()
