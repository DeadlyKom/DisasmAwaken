"""Извлечение подтверждённого динамическим CALL кода CE5D из исходной 71-байтовой области."""
from pathlib import Path
import collections
import contextlib
import io
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'),str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
from InspectZ80 import decoder
from CheckControlsTextQueue import base_memory
from SourcePresentation import format_function


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read('ControlsPointRespawnVerification')
    assert proof['passed'] and any(item['entry']==0xCE5D for item in proof['dynamic_call_reachability'])
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ControlsPointRespawnCode'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsPointRespawnCode'
    assert not candidate.exists() and not history.exists()
    flow,functions,symbols,source_map = read('ControlFlow'),read('Functions'),read('Symbols'),read('SourceMap')
    region = next(r for r in flow if r['name']=='Controls')
    assert not any(0xCE5D<=i['address']<0xCEA4 for i in region['instructions'])
    memory = base_memory()
    decoded = list(decoder(memory).disassemble(0xCE5D,0xCEA4,'h'))
    assert sum(len(i.bytes) for i in decoded)==71 and decoded[-1].operation=='RET'
    instructions = [dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=22,offset=i.address-0xC000) for i in decoded]
    targets = {int(m[1],16) for i in decoded if (m:=re.search(r'^(?:JP|JR) (?:NZ,|Z,|NC,|C,)?#([0-9A-F]{4})$',i.operation))}
    assert all(0xCE5D<=a<0xCEA4 for a in targets)
    region['instructions'] += instructions
    region['instructions'].sort(key=lambda i:(i['slot'],i['offset']))
    region['roots'] = sorted(set(region['roots'])|{0xCE5D})
    region['branches'] = sorted(set(region['branches'])|targets)
    region['instruction_count'] += len(instructions)
    region['code_bytes'] += 71
    region['classified_fraction'] = region['code_bytes']/region['total_bytes']
    function = dict(region='Controls',name='UnknownCE5D',address=0xCE5D,slot=22,offset=0xE5D,
        description='Unknown, назначение этого фрагмента ещё не установлено',semantic_status='unknown',
        end_offset=0xEA4,path='Source/Controls/UnknownCE5D.asm')
    index = next(n for n,f in enumerate(functions) if f['region']=='Controls' and f['address']==0xCE16)
    functions.insert(index+1,function)
    additions = {'Controls.UnknownCE5D.Entry':0xCE5D,**{'Controls.UnknownCE5D.Point'+format(a,'04X'):a for a in sorted(targets)}}
    assert not any(name in symbols for name in additions)
    symbols.update(additions)
    labels = {a:name for name,a in additions.items()}
    lines = ['                module Controls','                module UnknownCE5D',
        '                ; Документация [динамический вход](../../Docs/ControlsPointRespawn.md)',
        '                ; Код исходного CE5D подтверждён изменяемыми CALL, смысловой договор публикуется отдельно']
    for i in decoded:
        operation = i.operation.replace(',',', ')
        if operation.startswith(('JR ','JP ')):
            operation = re.sub(r'#([0-9A-F]{4})',lambda m:'@'+labels[int(m[1],16)],operation)
        name = labels.get(i.address,'').rsplit('.',1)[-1]
        lines.append(((name+':').ljust(16) if name else ' '*16)+operation)
    lines += ['                endmodule','                endmodule']
    pending = {ROOT / function['path']:format_function('\n'.join(lines)+'\n').encode('utf-8')}
    item = next(i for i in source_map if i['slot']==22 and i['offset']==0xE5D)
    assert item['kind']=='unclassified' and item['length']==71
    previous = ROOT / item['path']
    original = previous.read_bytes()
    assert original==bytes(memory[0xCE5D:0xCEA4])
    item.update(kind='code',origin=0xCE5D,path=function['path'])
    modified = read('ModifiedCode')
    for writer,target,owner,operation,path in ((0xCE61,0xCE5E,0xCE5D,'LD A,#00',function['path']),
        (0xCC4A,0xCE65,0xCE64,'LD C,#00','Source/Controls/UnknownCB00.asm')):
        assert not any(i['region']=='Controls' and i['writer']==writer and i['target']==target for i in modified)
        modified.append(dict(region='Controls',writer=writer,target=target,target_instruction=owner,size=1,
            target_operation=operation,path=path,writer_bank=1,target_bank=1,target_region='Controls',target_slot=22))
    inventory = read('Inventory')
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
        unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+len(instructions))
    inventory['ranges_by_kind'] = dict(collections.Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('ControlFlow',flow),('Functions',functions),('Symbols',symbols),('SourceMap',source_map),('ModifiedCode',modified),('Inventory',inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/'+stem+'.json')] = encode(value)
    path = ROOT / 'Source/Files/22_CONTROL0.inc'
    text = path.read_text('utf-8')
    needle = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/22_CONTROL0/Unclassified001.bin"'
    assert text.count(needle)==1
    pending[path] = text.replace(needle,'                disp #CE5D\n                include "../Controls/UnknownCE5D.asm"\n                ent').encode('utf-8')
    path = ROOT / 'Docs/Functions.md'
    text = path.read_text('utf-8')
    row = '| #CE5D | [Controls.UnknownCE5D](../Source/Controls/UnknownCE5D.asm) | Unknown, назначение этого фрагмента ещё не установлено |\n'
    needle = '| #CEA4 | [Controls.UnknownCEA4]'
    assert text.count(needle)==1 and row not in text
    text = text.replace(needle,row+needle)
    text = re.sub(r'\| Controls \| 67 \| (\d+) \|',r'| Controls | 68 | \1 |',text)
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Docs/FunctionDetails/Controls.md'
    text = path.read_text('utf-8')
    block = ('## UnknownCE5D\n\n[Controls.UnknownCE5D](../../Source/Controls/UnknownCE5D.asm)\n\n'
        'Unknown, назначение этого фрагмента ещё не установлено.\n\n'
        'Вход `#CE5D`, запись 22, смещения `#0E5D..#0EA3`.\n\n'
        '- Прямые вызовы: нет непосредственных обращений.\n'
        '- Непосредственные чтения: R.\n'
        '- Непосредственные записи: `#CE5E`.\n'
        '- Ввод и вывод: нет.\n'
        '- Косвенное завершение: нет в этом фрагменте.\n\n')
    assert '## UnknownCE5D\n' not in text
    pending[path] = text.replace('## UnknownCEA4\n',block+'## UnknownCEA4\n').encode('utf-8')
    plan = [(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT / 'Source/Resources/22_CONTROL0').resolve())
    assert previous.read_bytes()==original==(history / previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report = dict(passed=True,extracted_code_bytes=71,new_instructions=len(instructions),new_registered_entry='CE5D',
        dynamic_calls_proved=True,physical_bytes_preserved=True,semantic_publication_pending=True,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsPointRespawnCodeClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
