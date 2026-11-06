"""Выделение доказанных 64 байтов DCE3 из исходного ресурса банка 1, соседние блоки сохранены."""
from collections import Counter
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory,payload
from InspectZ80 import decoder
from SourcePresentation import format_function
from VerifySources import main as verify


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ControlsStationPrepareVerification')['passed']
    source=payload(23);start,end,offset,end_offset=0xDCE3,0xDD23,0x205,0x245
    instructions=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=23,offset=i.address-0xDADE)
        for i in decoder(base_memory()).disassemble(start,end,'h')]
    assert b''.join(bytes.fromhex(i['hex']) for i in instructions)==source[offset:end_offset]
    assert instructions[-1]['operation']=='RET'
    flow,functions,symbols,source_map,inventory=[read(name) for name in ('ControlFlow','Functions','Symbols','SourceMap','Inventory')]
    region=next(r for r in flow if r['name']=='Controls')
    assert not any(start<=i['address']<end for i in region['instructions'])
    old=next(i for i in source_map if i['slot']==23 and i['offset']<=offset and end_offset<=i['offset']+i['length'])
    assert old['kind']=='unclassified' and old['offset']==0x1CB and old['length']==180
    previous=ROOT/old['path'];original=previous.read_bytes();assert original==source[0x1CB:0x27F]
    code_path='Source/Controls/UnknownDCE3.asm'
    pieces=[dict(old,offset=a,length=b-a,kind=kind,path=path,origin=origin,sha256=hashlib.sha256(source[a:b]).hexdigest())
        for a,b,kind,path,origin in ((0x1CB,offset,'unclassified','Source/Resources/23_CONTROL/Unclassified001_BeforeStationPrepare.bin',None),
        (offset,end_offset,'code',code_path,start),(end_offset,0x27F,'unclassified','Source/Resources/23_CONTROL/Unclassified001_AfterStationPrepare.bin',None))]
    source_map[source_map.index(old):source_map.index(old)+1]=pieces
    region['instructions']=sorted(region['instructions']+instructions,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{start});region['instruction_count']+=len(instructions)
    region['code_bytes']+=64;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    description='Unknown, назначение этого фрагмента ещё не установлено'
    function=dict(region='Controls',name='UnknownDCE3',address=start,slot=23,offset=offset,end_offset=end_offset,
        path=code_path,description=description,semantic_status='unknown')
    index=next(i for i,f in enumerate(functions) if f['region']=='Controls' and f['address']>start);following=functions[index]
    functions.insert(index,function);assert 'Controls.UnknownDCE3.Entry' not in symbols;symbols['Controls.UnknownDCE3.Entry']=start
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
        unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+len(instructions))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    lines=['                module Controls','                module UnknownDCE3',
        '                ; Документация [проверка переноса](../../Docs/ControlsStationPrepare.md)',
        '                ; '+description,'                ; In:',
        '                ;   Unknown, регистровый контракт ещё не доказан',
        '                ; Out:', '                ;   исходные инструкции подготовки режима',
        '                ; Corrupt:', '                ;   Unknown, точный договор публикуется после выделения исходных байтов']
    lines += [('Entry:'.ljust(16) if index==0 else ' '*16)+item['operation'].replace(',',', ') for index,item in enumerate(instructions)]
    lines+=['                endmodule','                endmodule']
    pending={ROOT/code_path:format_function('\n'.join(lines)+'\n',None).encode('utf-8')}
    for piece in pieces:
        if piece['kind']!='code':pending[ROOT/piece['path']]=source[piece['offset']:piece['offset']+piece['length']]
    for name,value in (('ControlFlow',flow),('Functions',functions),('Symbols',symbols),('SourceMap',source_map),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Source/Files/23_CONTROL.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/23_CONTROL/'+previous.name+'"';assert text.count(needle)==1
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+needle,needle)
    replacement=('                ; Unknown, соседние исходные байты перед подготовкой станции\n'
        '                incbin "../Resources/23_CONTROL/Unclassified001_BeforeStationPrepare.bin"\n'
        '                assert $ == #0205\n                disp #DCE3\n                include "../Controls/UnknownDCE3.asm"\n                ent\n'
        '                assert $ == #0245\n                ; Unknown, переносимый загрузочный блок после подготовки станции\n'
        '                incbin "../Resources/23_CONTROL/Unclassified001_AfterStationPrepare.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Controls' for f in functions);described=sum(f['region']=='Controls' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Controls \| \d+ \| \d+ \|',f'| Controls | {total} | {described} |',text)
    needle='| #'+format(following['address'],'04X')+' | [Controls.'+following['name']+']';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #DCE3 | [Controls.UnknownDCE3](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Controls.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    block='## UnknownDCE3\n\n[Controls.UnknownDCE3](../../'+code_path+')\n\n'+description+'.\n\n'
    pending[path]=text.replace(needle,block+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsStationPrepareCode';history=ROOT/'Tools/Disasm/Research/History/BeforeControlsStationPrepareCode'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка неизменности текущих ручных файлов перед заменой.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённого ресурса после сверки исходных байтов и сохранённой копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/23_CONTROL').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    result=dict(passed=True,extracted_code_bytes=64,new_instructions=len(instructions),physical_bytes_preserved=True,
        code_reached_from_Action_TransferToStationLoader=True,neighbor_bytes_preserved=116,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsStationPrepareCodeClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
