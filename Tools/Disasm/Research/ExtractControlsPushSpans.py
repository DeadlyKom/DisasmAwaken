"""Расширение трёх неизвестных рисователей доказанными динамическими цепочками, без смены их статуса."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import re
import sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from InspectZ80 import decoder
from CheckControlsTextQueue import base_memory
import ControlsPushSpansFacts as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof=read('ControlsPushSpansVerification')
    assert proof['passed'] and all(len(v)==17 for v in proof['dynamic_targets'].values())
    flow,functions,symbols,source_map,inventory=(read(n) for n in ('ControlFlow','Functions','Symbols','SourceMap','Inventory'))
    region=next(r for r in flow if r['name']=='Controls')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsPushSpans'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsPushSpans'
    assert not candidate.exists() and not history.exists()
    pending,removed={},{}
    memory=base_memory()
    additions=[]
    # Регистрация динамических входов внутри существующих функций, новые функции не создаются.
    for entry,start,end in ((0xD633,0xD717,0xD727),(0xD727,0xD80F,0xD833),(0xD833,0xD901,0xD925)):
        f=next(f for f in functions if f['region']=='Controls' and f['address']==entry)
        assert f['semantic_status']=='unknown' and f['end_offset']==start-0xC000
        decoded=list(decoder(memory).disassemble(start,end,'h'))
        assert all(i.operation=='PUSH AF' for i in decoded[:16])
        assert sum(len(i.bytes) for i in decoded)==end-start
        assert not any(start<=i['address']<end for i in region['instructions'])
        additions.extend(dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=22,offset=i.address-0xC000) for i in decoded)
        for address,name in sorted(facts.LABELS.items()):
            region_name,pc=address
            if start<=pc<end:
                key='Controls.'+f['name']+'.'+name
                assert key not in symbols
                symbols[key]=pc
        code=next(i for i in source_map if i['path']==f['path'])
        raw=next(i for i in source_map if i['slot']==22 and i['offset']==start-0xC000)
        assert raw['kind']=='unclassified' and raw['length']==end-start
        previous=ROOT/raw['path']
        original=previous.read_bytes()
        assert original==bytes(memory[start:end])
        removed[previous]=original
        source_map.remove(raw)
        f['end_offset']=end-0xC000
        code['length']=f['end_offset']-f['offset']
        code['sha256']=hashlib.sha256(bytes(memory[f['address']:end])).hexdigest()
        path=ROOT/f['path']
        text=path.read_text('utf-8')
        text=text.replace('..#'+format(start-0xC001,'04X'),'..#'+format(end-0xC001,'04X'),1)
        # Добавление адресных пояснений только к исследованному входу быстрого заполнения.
        setup={0xD633:0xD706,0xD727:0xD7FE,0xD833:0xD8F0}[entry]
        needle='Point'+format(setup,'04X')+':'
        assert text.count(needle)==1
        before=facts.COMMENTS[setup][0]
        text=text.replace(needle,''.join('                ; '+note+'\n' for note in before)+needle,1)
        text=facts.name_operands('Controls',entry,text)
        marker='                endmodule\n                endmodule'
        assert text.count(marker)==1
        lines=[]
        address_labels={a:name for name,a in symbols.items() if name.startswith('Controls.')}
        for instruction in decoded:
            pc=instruction.address
            before,right=facts.COMMENTS.get(pc,([],None))
            lines.extend('                ; '+note for note in before)
            operation=instruction.operation.replace(',',', ')
            if operation.startswith(('JR ','JP ','CALL ')):
                operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+address_labels[int(m[1],16)],operation)
            operation=facts.name_operands('Controls',entry,operation)
            label=facts.LABELS.get(('Controls',pc),'')
            line=((label+':').ljust(16) if label else ' '*16)+operation
            if right:
                assert len(line)<80
                line=line.ljust(80)+'; '+right
            lines.append(line)
            if operation.startswith(('JR ','JP ','RET')):
                lines.append('')
        if entry==0xD633:
            lines+=['                ; JP @Controls.UnknownD727.Entry, продолжение в UnknownD727.asm','']
        lines+=['                ; -----------------------------------------','']
        pending[path]=text.replace(marker,'\n'.join(lines)+'\n'+marker).encode('utf-8')
        path=ROOT/'Source/Files/22_CONTROL0.inc'
        text=pending.get(path,path.read_bytes()).decode('utf-8')
        needle=('                ent\n                assert $ == #'+format(start-0xC000,'04X')+'\n'
            '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/22_CONTROL0/'+previous.name+'"')
        assert text.count(needle)==1
        pending[path]=text.replace(needle,'                ent').encode('utf-8')
        path=ROOT/'Docs/FunctionDetails/Controls.md'
        text=pending.get(path,path.read_bytes()).decode('utf-8')
        text=text.replace('#'+format(f['offset'],'04X')+'..#'+format(start-0xC001,'04X'),
            '#'+format(f['offset'],'04X')+'..#'+format(end-0xC001,'04X'))
        pending[path]=text.encode('utf-8')
    assert len(additions)==64
    region['instructions']=sorted(region['instructions']+additions,key=lambda i:(i['slot'],i['offset']))
    region['instruction_count']+=64
    region['code_bytes']+=88
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    region['branches']=sorted(set(region['branches'])|{0xD82E,0xD920})
    inventory['instructions']+=64
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('ControlFlow',flow),('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Source/Files/22_CONTROL0.inc'
    text=pending[path].decode('utf-8')
    for index,name in enumerate(('UnknownD633','UnknownD727')):
        needle='                include "../Controls/'+name+'.asm"'
        assert text.count(needle)==1
        text=text.replace(needle,needle.ljust(80)+'; ('+str(index)+') жёсткий порядок, продолжение цепочки PUSH AF')
    pending[path]=text.encode('utf-8')
    path=ROOT/'Source/Controls/UnknownD633.asm'
    text=pending[path].decode('utf-8')
    pending[path]=text.replace('                ; вычисление изменяемого смещения JR',
        '                ; (0) порядок перед UnknownD727.asm обязателен для продолжения после последнего PUSH\n                ; вычисление изменяемого смещения JR',1).encode('utf-8')
    path=ROOT/'Source/Controls/UnknownD727.asm'
    text=pending[path].decode('utf-8')
    pending[path]=text.replace('Entry:', '                ; (1) продолжение цепочки после UnknownD633.asm, CPU-стек ещё направлен в растр\nEntry:',1).encode('utf-8')
    # Добавление подтверждённых внутренних потоков в анализатор без создания новых корней функций.
    path=ROOT/'Tools/Disasm/Research/Analyze.py'
    text=path.read_text('utf-8')
    needle='    if name == "Music":'
    assert text.count(needle)==1
    hook=('    if name == "Controls":\n'
        '        # Цепочки PUSH AF подтверждены динамическими JR и моделью восстановления CPU-стека.\n'
        '        for start in (0xD717, 0xD80F, 0xD901):\n'
        '            assert memory[start:start+16] == bytes([0xF5])*16\n'
        '        observed = set(observed) | {0xD717, 0xD80F, 0xD901}\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py'
    text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)'
    assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = controls_push_spans_name_operands(region, function_address, operation)')
    text+='\nfrom ControlsPushSpansFacts import LABELS as CONTROLS_PUSH_SPANS_LABELS, name_operands as controls_push_spans_name_operands\nLABELS.update(CONTROLS_PUSH_SPANS_LABELS)\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py'
    text=path.read_text('utf-8')
    needle='\n\nif __name__ == "__main__":'
    assert text.count(needle)==1
    hook='\nfrom ControlsPushSpansFacts import COMMENTS as CONTROLS_PUSH_SPANS_COMMENTS\nREGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_PUSH_SPANS_COMMENTS)\n'
    pending[path]=text.replace(needle,'\n'+hook+needle).encode('utf-8')
    # Сохранение отдельного кандидата и проверка неизменности всех заменяемых файлов.
    plan=[(p,p.read_bytes(),after) for p,after in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before
    for path,before in {**{p:b for p,b,_ in plan},**removed}.items():
        target=history/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path,before in removed.items():
        assert path.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
        assert path.read_bytes()==before==(history/path.relative_to(ROOT)).read_bytes()
        path.unlink()
    result=dict(passed=True,extracted_code_bytes=88,original_instructions_added=64,
        functions_added=0,semantic_status_of_three_rasterizers='unknown',physical_bytes_preserved=True,
        independent_model_cases=proof['total_cases'],whole_rasterizer_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsPushSpansClassification.json').write_bytes(encode(result))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    if '--complete' in sys.argv:
        # Повтор записи только точного кандидата после прерывания файловой операции Windows.
        candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsPushSpans'
        history=ROOT/'Tools/Disasm/Research/History/BeforeControlsPushSpans'
        plan=[]
        for snapshot in candidate.rglob('*'):
            if not snapshot.is_file():
                continue
            relative=snapshot.relative_to(candidate)
            path=ROOT/relative
            assert path.resolve().is_relative_to(ROOT.resolve())
            before=(history/relative).read_bytes()
            after=snapshot.read_bytes()
            current=path.read_bytes()
            assert current in (before,after), relative
            plan.append((path,current,after))
        for path,current,after in plan:
            assert path.read_bytes()==current
            if current!=after:
                path.write_bytes(after)
        with contextlib.redirect_stdout(io.StringIO()):
            verify()
        for name in ('Unclassified007.bin','Unclassified008.bin','Unclassified009.bin'):
            path=ROOT/'Source/Resources/22_CONTROL0'/name
            assert path.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
            assert path.read_bytes()==(history/path.relative_to(ROOT)).read_bytes()
            path.unlink()
        proof=json.loads((ROOT/'Tools/Disasm/Reports/ControlsPushSpansVerification.json').read_text('utf-8'))
        result=dict(passed=True,extracted_code_bytes=88,original_instructions_added=64,
            functions_added=0,semantic_status_of_three_rasterizers='unknown',physical_bytes_preserved=True,
            independent_model_cases=proof['total_cases'],whole_rasterizer_proved=False,assembly_executed=False)
        (ROOT/'Tools/Disasm/Reports/ControlsPushSpansClassification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
    else:
        main()
