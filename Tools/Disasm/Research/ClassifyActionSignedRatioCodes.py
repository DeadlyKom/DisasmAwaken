"""Защищённая типизация 256 исходных кодов, соседние 18 байтов не объявляются разобранными."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionSignedRatioCodesData as facts


def main():
    def read(name):return json.loads((ROOT/f'Tools/Disasm/Reports/{name}.json').read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionSignedRatioCodeVerification');assert proof['passed'] and read('ActionSignedRatioCodeClassification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();raw=facts.validate(source)
    text,labels=facts.render(source);assert facts.parse(text)==(raw,labels)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x3A00)
    assert old['kind']=='unclassified' and old['length']==274
    previous=ROOT/old['path'];original=previous.read_bytes();assert original==source[0x3A00:0x3B12]
    suffix='Source/Resources/17_ACTION/Unclassified020_AfterRatioCodes.bin'
    pieces=[dict(old,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
            (0x3A00,0x3B00,'typed_data',facts.TABLE[1],0x9A00),(0x3B00,0x3B12,'unclassified',suffix,None))]
    position=source_map.index(old);source_map[position:position+1]=pieces
    assert not any(key in symbols for key in labels);symbols.update(labels)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/suffix:source[0x3B00:0x3B12]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/f'Tools/Disasm/Reports/{name}.json']=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FSignedRatioCode' not in text
    block=('\n                ; Физический исходный код одного индекса знакового отношения\n'
        '                struct FSignedRatioCode\n'+
        'Code'.ljust(16)+'db #00'.ljust(64)+'; исходный код, смещения четырёх знаковых ветвей добавляет EncodeSignedRatio\n'
        '                ends\n                assert FSignedRatioCode == #01\n\n')
    head,tail=text.rsplit('                endif',1);pending[path]=(head+block+'                endif'+tail).encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"';assert text.count(needle)==1
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+needle,needle)
    replacement=('                disp #9A00\n                include "../Action/Data/SignedRatioCodes.asm"\n                ent\n'
        '                assert $ == #3B00\n                ; Unknown, следующие 18 байтов вне таблицы кодов отношения\n'
        '                incbin "../Resources/17_ACTION/Unclassified020_AfterRatioCodes.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка ровно 26 физических адресов классов, без соседних инструкций.'
    assert text.count(needle)==1 and 'signed_ratio_code_records' not in text
    hook='''    # Проверка 256 исходных кодов отношения, без генерации идеальной тригонометрической таблицы.
    from ActionSignedRatioCodesData import TABLE as RATIO_CODES, parse as parse_ratio_codes, validate as validate_ratio_codes
    signed_ratio_code_records = 0
    entries = [item for item in source_map if item['path'] == RATIO_CODES[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_ratio_codes((ROOT / RATIO_CODES[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (17,0x3A00,256,0x9A00)
        assert raw == validate_ratio_codes(sources[17])
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FSIGNEDRATIOCODE'] == 1 and symbols['FSIGNEDRATIOCODE.CODE'] == 0
        signed_ratio_code_records = 256

'''
    text=text.replace(needle,hook+needle);needle="    report['class_handler_records'] = class_handler_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,"    report['signed_ratio_code_records'] = signed_ratio_code_records\n"+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1 and 'SIGNED_RATIO_CODES_TABLE' not in text
    hook=('    # Двести пятьдесят шесть исходных кодов отношения, без тригонометрического пересчёта.\n'
        '    from ActionSignedRatioCodesData import TABLE as SIGNED_RATIO_CODES_TABLE, render as render_signed_ratio_codes\n'
        '    text, bindings = render_signed_ratio_codes(data_by_slot[17])\n'
        '    write(SIGNED_RATIO_CODES_TABLE[1], text)\n    symbols.update(bindings)\n'
        '    special[17, 0x3A00] = (0x3B00, SIGNED_RATIO_CODES_TABLE[1], 0x9A00)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8')
    pending[path]=(text+'\n## Исходные коды знакового отношения\n\n[SignedRatioCodes](../Source/Action/Data/SignedRatioCodes.asm) содержит 256 физических FSignedRatioCode размером один байт, поле Code по смещению 0. Исходные значения 9A00..9AFF сохранены буквально, потребитель описан в [кодировщике отношения](ActionSignedRatioCode.md). Стандартная тригонометрическая формула для генерации сборочных данных не применяется.\n').encode('utf-8')
    path=ROOT/'Docs/ActionSignedRatioCode.md';text=path.read_text('utf-8')
    pending[path]=(text+'\nТаблица оформлена как 256 физических [FSignedRatioCode](../Source/Action/Data/SignedRatioCodes.asm), поле Code занимает один байт. Все исходные значения, включая длинные повторяющиеся участки, сохранены, соседние 18 байтов не объявлены частью таблицы.\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8');line=next(v for v in text.splitlines() if '"| FClassHandler |' in v)
    row='| FSignedRatioCode | #01 | Code, 256 физических [SignedRatioCodes](../Source/Action/Data/SignedRatioCodes.asm), см. [ActionSignedRatioCode](ActionSignedRatioCode.md) |'
    pending[path]=text.replace(line,line+'\n'+line[:len(line)-len(line.lstrip())]+json.dumps(row,ensure_ascii=False)+',').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionSignedRatioCodes';history=ROOT/'Tools/Disasm/Research/History/BeforeActionSignedRatioCodes'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и контроль отсутствия новых ручных правок до замены.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого ресурса после сверки оригинала и защищённой копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    result=dict(passed=True,typed_bytes=256,physical_records=256,structure='FSignedRatioCode',
        original_sha256=facts.DIGEST,original_bytes_preserved=True,neighbor_bytes_preserved=18,
        observed_table_indices=len(proof['table_indices_observed']),formula_used_to_generate_build_data=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionSignedRatioCodesClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
