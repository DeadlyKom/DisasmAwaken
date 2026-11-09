"""637 логических байтов текстов, 29 доказанных адресов и сохранённый секторный хвост."""
from collections import Counter
import contextlib,hashlib,io,json,sys
from CheckIntro import ROOT
import ControlsFlightMessages as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports';read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('ControlsFlightMessagesVerification');assert proof['passed'] and proof['total_cases']==1479 and proof['glyph_events']==29121
    source=(ROOT/'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes();rows=facts.records(source)
    sm,inventory,symbols,modified=[read(n) for n in ('SourceMap','Inventory','Symbols','ModifiedCode')]
    old=next(r for r in sm if r['slot']==23 and r['offset']==facts.START);assert old['length']==819 and old['kind']=='unclassified'
    old_path=ROOT/old['path'];raw=old_path.read_bytes();assert raw[:637]==source[facts.START:facts.END]
    assert not any(r.get('target_path')==old['path'] for r in modified)
    pending={ROOT/facts.PATH:raw[:637],ROOT/facts.TAIL_PATH:raw[637:]};assert all(not p.exists() for p in pending)
    pieces=[]
    for begin,end,path,kind in ((facts.START,facts.END,facts.PATH,'binary_resource'),(facts.END,0x1A00,facts.TAIL_PATH,'unclassified')):
        piece=dict(slot=23,offset=begin,length=end-begin,kind=kind,path=path,origin=None,sha256=hashlib.sha256(raw[begin-facts.START:end-facts.START]).hexdigest())
        if kind=='binary_resource':piece['format']=facts.FORMAT
        pieces.append(piece)
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm));inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',sm),('Inventory',inventory)):pending[reports/(name+'.json')]=encode(value)
    block='                ; Документация [строки текстовой очереди полёта](../../Docs/ControlsFlightMessages.md)\n                module ControlsFlightText\n'
    for row in rows:
        assert len(row['name'])<=15;key='ControlsFlightText.'+row['name'];assert key not in symbols;symbols[key]=row['address']
        meaning=row['raw'].decode('cp866').replace('\r',' / ').replace('\n','')
        block+=(row['name'].ljust(16)+'equ #'+format(row['address'],'04X')).ljust(80)+'; '+meaning+'\n'
    block+='                endmodule\n\n'
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8');pending[reports/'Symbols.json']=encode(symbols)
    path=ROOT/'Source/Files/23_CONTROL.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/23_CONTROL/'+old_path.name+'"';assert text.count(needle)==1
    replacement='                ; Документация [29 сообщений и секторный хвост](../../Docs/ControlsFlightMessages.md)\n                incbin "../Controls/Resources/FlightMessages.bin"\n                assert $ == #194A\n                ; Unknown, 182 байта хвоста секторов после логического конца CONTROL\n                incbin "../Resources/23_CONTROL/'+facts.TAIL_PATH.rsplit('/',1)[-1]+'"'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    binary_resources[7, 0x2900]';assert text.count(needle)==1
    hook='    # Строки текстовой очереди ограничены логическим концом CONTROL.\n    from ControlsFlightMessages import START as FLIGHT_TEXT_START,END as FLIGHT_TEXT_END,PATH as FLIGHT_TEXT_PATH,FORMAT as FLIGHT_TEXT_FORMAT,TAIL_PATH as FLIGHT_TEXT_TAIL_PATH,records as flight_text_records\n    binary_resources[23,FLIGHT_TEXT_START]=(FLIGHT_TEXT_END,FLIGHT_TEXT_PATH,FLIGHT_TEXT_FORMAT)\n    for row in flight_text_records(data_by_slot[23]):symbols["ControlsFlightText."+row["name"]]=row["address"]\n'
    text=text.replace(needle,hook+needle);needle='                path = ROOT / binary_path';assert text.count(needle)==1
    text=text.replace(needle,'                if slot==23 and begin==FLIGHT_TEXT_END:binary_path=FLIGHT_TEXT_TAIL_PATH\n'+needle);pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка всех 29 строк, исходного CP866, терминаторов и именованных адресов CONTROL.
    import ControlsFlightMessages as flight_text
    flight_rows=flight_text.records(sources[23])
    assert (ROOT/flight_text.PATH).read_bytes()==sources[23][flight_text.START:flight_text.END]
    for row in flight_rows:assert symbols[('ControlsFlightText.'+row['name']).upper()]==row['address']

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    lines=['# Сообщения текстовой очереди полёта','',
      '[Исходный блок строк](../'+facts.PATH+'), [физический состав CONTROL](../Source/Files/23_CONTROL.inc), [именованные адреса](../Includes/Const/Include.inc).',
      '[Разметка](../Tools/Disasm/Research/ControlsFlightMessages.py), [проверка](../Tools/Disasm/Research/CheckControlsFlightMessages.py), [договор потребителя](ControlsTextDisplay.md).','',
      '637 байтов F1AB..F427 содержат 29 действующих строк CP866. LF завершает строку, CR вызывает прокрутку и продолжает тот же вызов потребителя. Нулевой байт потребитель считал бы обычным знаком, здесь он терминатором не используется. Все исходные CR, LF и пробелы сохранены.','',
      'Логический CONTROL заканчивается по файловому смещению 194A. Следующие 182 байта выделенных секторов содержат повторяющийся текст и обрезанный конец, они сохраняются отдельным неизвестным хвостом. Их чтение во время игры либо неиспользуемость этим разбором не объявляются доказанными.','',
      '| Имя | Адрес | Байтов | Текст, CR показан как / |','| --- | --- | --- | --- |']
    for row in rows:lines.append('| '+row['name']+' | '+format(row['address'],'04X')+' | '+str(row['length'])+' | '+row['raw'].decode('cp866').replace('\r',' / ').replace('\n','')+' |')
    lines+=['','1479 сценариев выполняют все строки настоящим ConsumeTextQueue с шрифтом и прокруткой, три начальные колонки 0, 23 и 255, все 17 положений курсора записи. После постановки курсор чтения направлен перед фактически выбранной записью, чтобы каждая строка действительно выводилась целиком. Подтверждены 29121 знак и 2873 прокрутки. Сверены восемь банков RAM кроме 66 байтов обычного стека и двух байтов SavedSP прокрутки, проверено сохранение IX/IY. Полные регистры, R, такты, общая кратность записей, IRQ, сборка и нативная игра не проверялись.']
    pending[ROOT/'Docs/ControlsFlightMessages.md']=('\n'.join(lines)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsFlightMessages';history=ROOT/'Tools/Disasm/Research/History/BeforeControlsFlightMessages';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before in {**{p:b for p,b,_ in plan if b is not None},old_path:raw}.items():
        q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/23_CONTROL').resolve()) and old_path.read_bytes()==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,strings=29,logical_bytes=637,sector_tail_preserved=182,named_addresses=29,model_cases=1479,
        all_original_bytes_and_physical_layout_preserved=True,assembly_executed=False,native_execution=False)
    (reports/'ControlsFlightMessagesClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
