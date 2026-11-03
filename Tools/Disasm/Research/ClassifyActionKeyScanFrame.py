"""Добавление только пяти подтверждённых инструкций из семи байтов, без массового экспорта."""
from collections import Counter
import contextlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
import ActionKeyScanFrameFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionKeyDispatchPrefixVerification')
    assert proof['passed'] and proof['raw_return_epilogue_separate_cases']==65536
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    original=source[0x118B:0x1192]
    assert original==bytes.fromhex('dd e1 c1 d1 e1 18 d3')
    flow,functions,symbols,source_map,inventory=[read(n) for n in ('ControlFlow','Functions','Symbols','SourceMap','Inventory')]
    region=next(r for r in flow if r['name']=='Action')
    records=[dict(address=a,operation=op,hex=raw,slot=17,offset=offset) for a,op,raw,offset in (
        (0x6F4E,'POP IX','dde1',0x118B),(0x6F50,'POP BC','c1',0x118D),
        (0x6F51,'POP DE','d1',0x118E),(0x6F52,'POP HL','e1',0x118F),(0x6F53,'JR #6F28','18d3',0x1190))]
    assert not any(0x6F4E<=i['address']<0x6F55 for i in region['instructions'])
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==original
    assert any(i['address']==0x6F28 for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0x6F4E})
    region['branches']=sorted(set(region['branches'])|{0x6F28})
    region['instruction_count']+=5;region['code_bytes']+=7
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    name,description=facts.FUNCTIONS[0x6F4E];path_string='Source/Action/'+name+'.asm'
    assert not any(f['region']=='Action' and f['address']==0x6F4E for f in functions)
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']==0x6F1D)+1
    functions.insert(index,dict(region='Action',name=name,address=0x6F4E,slot=17,offset=0x118B,
        description=description,semantic_status='described',end_offset=0x1192,path=path_string))
    assert 'Action.'+name+'.Entry' not in symbols
    symbols['Action.'+name+'.Entry']=0x6F4E
    item=next(i for i in source_map if i['slot']==17 and i['offset']==0x118B)
    assert (item['length'],item['kind'],item['path'])==(7,'unclassified','Source/Resources/17_ACTION/Unclassified016.bin')
    previous=ROOT/item['path'];assert previous.read_bytes()==original
    item.update(kind='code',path=path_string,origin=0x6F4E)
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
        instructions=inventory['instructions']+5)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
        for kind in inventory['ranges_by_kind']}
    pending={}
    for stem,value in (('ControlFlow',flow),('Functions',functions),('Symbols',symbols),('SourceMap',source_map),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    lines=['                module Action','                module '+name,
        '                ; Документация [рамка клавиатурного сканирования](../../Docs/ActionKeyDispatchPrefix.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, банк 5, перенесённые 6F4E..6F54, смещения 118B..1191']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0x6F4E]):
        lines+=['                ; '+heading+':']+['                ;   '+value for value in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        before,right=facts.COMMENTS.get(record['address'],([],None))
        lines+=['                ; '+text for text in before]
        op=record['operation'].replace('JR #6F28','JR @Action.Unknown6F1D.Point6F28')
        lines.append(('Entry:          ' if record['address']==0x6F4E else ' '*16)+op)
    lines+=['                endmodule','                endmodule']
    assert not (ROOT/path_string).exists()
    pending[ROOT/path_string]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle=('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/17_ACTION/Unclassified016.bin"')
    assert text.count(needle)==1
    pending[path]=text.replace(needle,'                ; Подтверждённый хвост восстановления рамки клавиатуры\n'
        '                disp #6F4E\n                include "../Action/RestoreKeyScanFrame.asm"\n                ent').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionKeyScanFrameFacts import FUNCTIONS as ACTION_KEY_SCAN_FRAME_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_KEY_SCAN_FRAME_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionKeyScanFrameFacts import CONTRACTS as ACTION_KEY_SCAN_FRAME_CONTRACTS\nCONTRACTS.update(ACTION_KEY_SCAN_FRAME_CONTRACTS)\n"),
        ('SemanticNames.py',"\nDOCUMENTS['Action',0x6F4E]=('ActionKeyDispatchPrefix','рамка клавиатурного сканирования')\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8')
        assert extra.strip().splitlines()[0] not in text
        pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":'
    assert text.count(needle)==1
    hook="\nfrom ActionKeyScanFrameFacts import COMMENTS as ACTION_KEY_SCAN_FRAME_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_KEY_SCAN_FRAME_COMMENTS)\n"
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8')
    total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #6F55 |';line='| #6F4E | [Action.'+name+'](../'+path_string+') | '+description+' |\n'
    assert text.count(needle)==1
    pending[path]=text.replace(needle,line+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## Unknown6F55\n'
    assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+path_string+')\n\n'+description+'.\n\nВход `#6F4E`, запись 17, смещения `#118B..#1191`.\n\n[Рамка и отдельная проверка хвоста](../ActionKeyDispatchPrefix.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionKeyScanFrame';history=ROOT/'Tools/Disasm/Research/History/BeforeActionKeyScanFrame'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата, до изменения активных реестров.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только семи заменённых байтов после подтверждения их исходной копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,confirmed_code_bytes=7,confirmed_instructions=5,described_functions=1,
        new_memory_allocated=False,physical_bytes_preserved=True,
        proof_report='ActionKeyDispatchPrefixVerification.json',proof_case_subset='restore_frame',
        proof_case_count=65536,additional_model_run=False,unknown_dispatcher_status_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionKeyScanFrameClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
