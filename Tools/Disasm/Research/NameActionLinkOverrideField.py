"""Доказанное поле подстановки связи, сохранение раскладки и посторонних Unknown15."""
import contextlib,importlib,io,json,os,re,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify

NAME='LinkOverride'
NOTE='числовой индекс подстановки LinkedIndex, FF запрещает подстановку, ноль разрешён и возвращает Z'


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports'
    proof=json.loads((reports/'ActionLinkOverrideVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==72192 and proof['all_override_bytes_and_input_F']
    assert proof['ff_is_no_override'] and proof['non_ff_copied_to_linked_index']
    # Проверка всех уже декодированных индексных обращений, это не исключает неустановленные косвенные обращения.
    flow=json.loads((reports/'ControlFlow.json').read_text('utf-8'))
    accesses=[i for r in flow if r['name']=='Action' for i in r['instructions'] if re.search(r'\(I[XY]\+#15\)',i['operation'])]
    assert {i['address'] for i in accesses}=={0x662B,0x7921,0x7A73,0x7DF0,0xE908,0xF479,0xF58C}
    assert [i for i in accesses if not i['operation'].startswith('LD (')]==[next(i for i in accesses if i['address']==0x662B)]
    assert all('#FF' in i['operation'] for i in accesses if i['address'] not in (0x662B,0xF58C))
    pending={}
    # Обновление только контекста FActionRecord, одноимённые поля ControlOptions не затрагиваются.
    paths=list((ROOT/'Source/Action').glob('*.asm'))
    paths+=list((ROOT/'Tools/Disasm/Research').glob('*Facts.py'))
    paths+=list((ROOT/'Docs').glob('Action*.md'))
    for path in paths:
        text=path.read_text('utf-8')
        if 'Unknown15' not in text:continue
        if path.name.endswith('Facts.py') and 'FActionRecord' not in text:continue
        after=text.replace('Unknown15',NAME)
        after=after.replace('LinkOverride и StateCode сохраняют неизвестные имена, глобальное игровое назначение этих полей ещё не доказано',
            'LinkOverride задаёт индекс подстановки связи, конкретная игровая роль связи и состояния зависит от класса')
        pending[path]=after.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ConfirmedIndexedFields.py';text=path.read_text('utf-8')
    assert 'FActionRecord.Unknown15' in text
    pending[path]=text.replace('FActionRecord.Unknown15','FActionRecord.'+NAME).encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    needle=('Unknown15'.ljust(16)+'db #00').ljust(80)+'; игровой смысл ещё неизвестен'
    assert text.count(needle)==1
    pending[path]=text.replace(needle,(NAME.ljust(16)+'db #00').ljust(80)+'; '+NOTE).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ActionObjectRecords.py';text=path.read_text('utf-8')
    assert text.count('KNOWN={')==1 and '21:(' not in text
    pending[path]=text.replace('KNOWN={',"KNOWN={21:('"+NAME+"','"+NOTE+"'),\n       ").encode('utf-8')
    path=ROOT/'Source/Action/Data/ObjectRecords.asm';text=path.read_text('utf-8')
    needle='; Unknown15, игровой смысл ещё неизвестен';assert text.count(needle)==26
    pending[path]=text.replace(needle,'; '+NAME+', '+NOTE).encode('utf-8')
    path=reports/'Symbols.json';symbols=json.loads(path.read_text('utf-8'));renamed=0
    for key in tuple(symbols):
        if key.startswith('ActionObjectRecords.') and key.endswith('.Unknown15'):
            new=key.rsplit('.',1)[0]+'.'+NAME;assert new not in symbols
            symbols[new]=symbols.pop(key);renamed+=1
    assert renamed==26
    assert 'ControlOptions.Missile3' in symbols
    pending[path]=(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    path=ROOT/'Docs/ActionObjectRecords.md';text=pending.get(path,path.read_bytes()).decode('utf-8')
    needle='| 16 | SavedStateCode |';assert text.count(needle)==1
    text=text.replace(needle,'| 15 | LinkOverride | Индекс подстановки LinkedIndex, FF запрещает, ноль разрешён |\n'+needle)
    text+='\n## Индекс подстановки связи\n\n[LinkOverride](ActionLinkOverride.md) по смещению 15 является числовым байтом, разряды 7..0 не объявляются независимыми флагами. '
    text+='FF запрещает запись, 00..FE копируются в LinkedIndex с выбором State02. Ноль записывается и возвращает Z, поэтому некоторые родительские обработчики продолжают обычный выбор связи. '
    text+='Пять установленных писателей записывают FF, State08 переносит сюда Unknown0D текущей записи. Значение самого Unknown0D не переименовывается. '
    text+='Сверены семь известных прямых индексных обращений, все 26 физических экземпляров и 72192 сценария читателя. Неустановленные косвенные обращения и игровой смысл всех связей этим не исключены.\n'
    pending[path]=text.encode('utf-8')
    # Уточнение прежней границы описания после установления числового назначения поля.
    path=ROOT/'Docs/ActionLinkOverride.md';text=pending[path].decode('utf-8')
    old='02. Назначение этого кода и глобальный игровой смысл LinkOverride пока'
    if old in text:text=text.replace(old,'02. Конкретная игровая роль связи и состояния для всех классов пока')
    text+='\nПоле структуры теперь называется LinkOverride, его адрес и размер не изменены. '
    text+='Известные писатели по 7921, 7A73, 7DF0, E908 и F479 записывают FF, по F58C записывается Unknown0D родителя до проверки активности цели. '
    text+='Это имя описывает доказанный механизм подстановки, а не принадлежность объекта к игровому классу.\n'
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionLinkOverrideField'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionLinkOverrideField'
    assert not candidate.exists() and not history.exists()
    before={p:p.read_bytes() for p in pending}
    for folder,values in ((candidate,pending),(history,before)):
        for path,data in values.items():
            target=folder/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path,data in before.items():assert path.read_bytes()==data
    for path,data in pending.items():
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='link-field-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(data)
            os.replace(temporary,path)
        else:path.write_bytes(data)
    importlib.reload(sys.modules['ActionObjectRecords'])
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    from ActionObjectRecords import layout
    size,fields=layout('FActionRecord');assert size==64 and fields[NAME]==21
    result=dict(passed=True,field=NAME,field_offset=21,record_size=64,physical_symbols_renamed=renamed,
        known_indexed_accesses=accesses,files_changed=len(pending),model_cases=72192,
        no_request_value=255,zero_is_allowed_value=True,zero_returns_Z=True,bit_flags_assumed=False,
        other_structures_Unknown15_preserved=True,original_instruction_bytes_and_physical_records_preserved=True,
        all_indirect_accesses_excluded=False,full_game_meaning_of_all_links_proved=False,
        assembly_executed=False,native_execution=False)
    (reports/'ActionLinkOverrideFieldNaming.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='known_indexed_accesses'},indent=2))


if __name__=='__main__':main()
