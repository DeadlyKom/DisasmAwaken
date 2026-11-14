"""Четыре суффикса двух пороговых входов и полные обёртки выражения.

Документация: ../../../Docs/EntryThreshold.md
"""
from hashlib import sha256
import json
import sys

from CheckEntryThreshold import ROOT, Simulator, get_registers
from CheckGeometryReturnEntries import Memory
from CheckGlyphRenderer import compare_flags
from CheckMarketAccess import add16_flags


def main(with_expression_wrappers=False):
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    original = bytearray(65536)
    for slot, destination in ((4, 0x6000), (5, 0xC000)):
        item = next(row for row in manifest['entries'] if row['slot'] == slot)
        source = (ROOT/(item['path']+'.sectors.bin')).read_bytes()
        assert source == disk[item['offset']:item['offset']+item['allocated_length']]
        assert sha256(source).hexdigest() == item['sectors_sha256']
        original[destination:destination+len(source)] = source
    # Проверка наблюдателя самостоятельной записью CPU.
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex('320070')
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(65536)
    cpu = Simulator(memory)
    initial = get_registers({'SP':0x7FFE, 'BC':0x365D, 'IX':0xB000, 'IY':0x5C3A,
        '^HL':0xB800, '^DE':0x47AD, '^BC':0x58BE, '^AF':0x69CF}, None, False)
    prefixes = [b''] + [str(n).encode() for n in range(257)] + [b'65535', b'99999']
    cases = 0
    counts = {symbol:0 for symbol in 'cvsk'}
    selector_overlap_cases = 0
    entries = ((0xC28F, 0xC9F8, 0xC29F, 0x7217, 0x71B9,
                0x9592, 0x95F1, 0x9400, 0x9849, 0x988E),
               (0xC2BB, 0xCA04, 0xC2CB, 0x73D8, 0x737D,
                0x95D4, 0x9633, 0x9484, 0x984A, 0x98F6))
    for entry, anchor, target, row, offset, prices, weights, restrictions, selector, limits in entries:
        # Чтение настоящих четырёх FScriptToken, порядок определяет оставшийся B.
        bindings = {}
        for position in range(4):
            address = anchor + 3*(position+1)
            symbol = chr(original[address])
            handler = int.from_bytes(original[address+1:address+3], 'little')
            bindings[symbol] = (4-position, handler)
        assert set(bindings) == set('cvsk')
        for prefix in prefixes:
            index = ((int(prefix)-1)&65535) if prefix else 36
            low_index = index & 255
            for symbol in 'cvsk':
                for pattern in range(5):
                    memory[:] = original
                    memory[row], memory[offset] = 29, 7
                    memory[selector] = (pattern*73)&255
                    raw = (0, 1, 127, 128, 255)[pattern]
                    # Создание данных только выбранного свойства, код LANG сохраняется.
                    if symbol in 'cv':
                        base = prices if symbol == 'c' else weights
                        address = base + 2*low_index
                        memory[address:address+2] = bytes((raw, (raw^0xA5)))
                        result = raw + ((raw^0xA5)*256 if symbol == 'c' else 0)
                        out_hl = address + int(symbol == 'c')
                        out_a = bindings[symbol][1]&255
                        flags = add16_flags(2*low_index, base, 0x40)
                    elif symbol == 's':
                        address = restrictions + 4*low_index
                        wanted = memory[selector]
                        record = [(wanted+1)&255]*4
                        if pattern < 4:
                            record[pattern] = wanted
                        memory[address:address+4] = bytes(record)
                        # Селектор читается после записи фикстуры, он может находиться внутри неё.
                        wanted = memory[selector]
                        found = record.index(wanted) if wanted in record else 4
                        result = int(found == 4)
                        out_hl = address + (found+1 if found < 3 else 3)
                        out_a = wanted
                        flags = compare_flags(wanted, record[min(found, 3)])
                        selector_overlap_cases += int(address <= selector < address+4)
                    else:
                        address = limits + low_index
                        memory[address] = raw
                        result = 1 if raw&128 else 127
                        out_hl = address
                        out_a = result
                        flags = 0x10 | (raw&0xA8) | (0 if raw&128 else 0x44)
                    text = prefix + b'.' + symbol.encode() + b'!\r'
                    memory[0xB000:0xB000+len(text)] = text
                    memory[0x7FFE:0x8000] = bytes((255, 63))
                    cpu.registers[:] = initial
                    r = cpu.registers
                    memory.writes.clear()
                    memory.recording = True
                    cpu.run(start=entry-6 if with_expression_wrappers else entry, stop=0x3FFF)
                    memory.recording = False
                    # Проверка результата, полного F и оставшегося счётчика таблицы в B.
                    assert (256*r[6]+r[7], 256*r[4]+r[5], r[2], r[3], r[0], r[1]) == (
                        out_hl, result, bindings[symbol][0], 36, out_a, flags), (entry, prefix, symbol, pattern, list(r))
                    assert r[12] == 0x8000 and 256*r[8]+r[9] == 0xB000+len(prefix)+2
                    assert r[10:12] == initial[10:12] and r[16:18] == initial[16:18]
                    assert r[18] == 4 and r[19] == initial[19]
                    persistent = [(0xC804, target&255), (0xC805, target>>8)]
                    if with_expression_wrappers:
                        persistent.extend(((0xB800, result&255), (0xB801, result>>8)))
                        assert (256*r[20]+r[21], 256*r[22]+r[23]) == (result, 0xB802)
                        assert bytes(memory[0x7FFC:0x7FFE]) == result.to_bytes(2, 'little')
                    else:
                        assert r[20:24] == initial[20:24]
                    # Проверка отсутствия банкового и рабочего эффекта прямой пороговой ветви.
                    lower = 0x7FF4 if with_expression_wrappers else 0x7FF6
                    assert [(a,v) for a,v in memory.writes if not lower <= a < 0x7FFE] == persistent
                    assert bytes(memory[0x7FFE:0x8000]) == bytes((255, 63))
                    cases += 1
                    counts[symbol] += 1
    result = dict(passed=True, method='original_threshold_suffix_dispatch_and_real_field_handlers',
        cases=cases, cases_by_suffix=counts, expression_wrappers_executed=with_expression_wrappers,
        all_low_index_bytes=True, all_suffixes_checked=True, selector_overlap_cases=selector_overlap_cases,
        full_output_flags_and_remaining_B_checked=True, exact_non_stack_write_sequence_checked=True,
        physical_disk_and_sector_hashes_checked=True, CPU_write_watch_positive_control=True,
        original_return_word_preserved=True, full_R_proved=False,
        all_input_values_registers_addresses_and_invalid_suffixes_checked=False,
        flat_RAM_model_without_banking=True, stack_bus_cycle_order_verified=False,
        irq_executed=False, native_execution=False, assembly_executed=False)
    name = 'EntryThresholdSuffixExpressionWrappersVerification.json' if with_expression_wrappers else 'EntryThresholdSuffixesVerification.json'
    (ROOT/'Tools/Disasm/Reports'/name).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main('--expression-wrappers' in sys.argv)
