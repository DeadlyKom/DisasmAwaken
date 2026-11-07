"""Дисковые состояния SAVE, смещения и различия относительно исходной станции."""
import json

from SavedStateLayout import ROOT, START, SIZE, SLOTS, structures, render, parse


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    source_map = json.loads((reports / 'SourceMap.json').read_text(encoding='utf-8'))
    station = (ROOT / 'Tools/Disasm/Extracted/Active/04_STATIONF.C.bin').read_bytes()
    initial = station[START - 0x6000:START - 0x6000 + SIZE]
    # Проверка констант фактического протокола, чтение и запись переносят два сектора с 983B.
    for path in ('HandleSaveSlotAction.asm', 'HandleLoadSlotAction.asm'):
        code = (ROOT / 'Source/Station' / path).read_text(encoding='utf-8').upper()
        assert 'LD HL, @SAVESLOTSTATE.BUFFER' in code
        assert 'LD B, @SAVESLOTCONST.SECTORCOUNT' in code
    variables = (ROOT / 'Includes/Variables/Include.inc').read_text(encoding='utf-8')
    constants = (ROOT / 'Includes/Const/Include.inc').read_text(encoding='utf-8')
    assert __import__('re').search(r'Buffer\s+equ #983B', variables)
    assert __import__('re').search(r'SectorCount\s+equ #02\b', constants)
    spans = [item for item in source_map if item['slot'] == 4 and item['kind'] == 'typed_data'
             and START - 0x6000 <= item['offset']
             and item['offset'] + item['length'] <= START - 0x6000 + SIZE]
    types = structures()
    slots = []
    for slot, name in SLOTS:
        data = (ROOT / f'Tools/Disasm/Extracted/Active/{slot}_{name}.s.bin').read_bytes()
        assert len(data) == SIZE
        differences = [index for index, (a, b) in enumerate(zip(data, initial)) if a != b]
        if name == 'SAVE5':
            assert data == bytes(SIZE)
        else:
            assert differences == [3]
        total = 0
        for span in spans:
            offset = span['offset'] - (START - 0x6000)
            candidate, _ = render(data, span, name, types)
            actual, _ = parse(candidate, types)
            assert actual == data[offset:offset + span['length']]
            total += len(actual)
        slots.append(dict(slot=slot, name=name, typed_bytes=total,
                          all_zero=data == bytes(SIZE), differences_from_station=differences,
                          timer_low=data[3], semantic_validity_proved=False))
    result = dict(passed=True, total_cases=len(slots), transfer_start=START, transfer_size=SIZE,
                  typed_spans_per_slot=len(spans), slots=slots,
                  unknown_bytes_per_slot=SIZE - total, assembly_executed=False)
    (reports / 'SavedStateLayoutVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'slots'}, indent=2))


if __name__ == '__main__':
    main()
