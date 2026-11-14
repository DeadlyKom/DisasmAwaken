"""Полные s/n двух читателей количества, без подмены банковых процедур.

Документация: ../../../Docs/WeightFields.md
"""
from hashlib import sha256
import json
import sys

from CheckEntryThreshold import ROOT, Simulator, get_registers, make_context, PortTrace, put
from CheckBank4Index import WriteMemory
from CheckActiveNeighbors import reference as neighbor_reference
from CheckWorldSignature import signature, step_key, logical_flags
from CheckGlyphRenderer import compare_flags


def main(with_expression_wrappers=False):
    _, _, original_banks = make_context()
    original_banks = [bytearray(bank) for bank in original_banks]
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    for slot in (4, 5, 7):
        item = next(row for row in manifest['entries'] if row['slot'] == slot)
        sectors = (ROOT/(item['path']+'.sectors.bin')).read_bytes()
        assert sectors == disk[item['offset']:item['offset']+item['allocated_length']]
        assert sha256(sectors).hexdigest() == item['sectors_sha256']
        if slot == 5:
            original_banks[6][:len(sectors)] = sectors
    # Проверка наблюдателя самостоятельной записью CPU.
    probe = WriteMemory(banks=[bytearray(0x4000) for _ in range(8)], out7ffd=0x16)
    put(probe, 0x4000, bytes.fromhex('320070'))
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.cpu_writes == [(0x7000, 0)]
    memory = WriteMemory(banks=[bank.copy() for bank in original_banks], out7ffd=0x16)
    cpu = Simulator(memory)
    initial = get_registers({'SP':0x7FFE, 'BC':0x365D, 'IX':0xB000, 'IY':0x5C3A,
        '^HL':0xB800, '^DE':0x47AD, '^BC':0x58BE, '^AF':0x69CF}, None, False)
    prefixes = [b''] + [str(n).encode() for n in range(257)] + [b'65535', b'99999']
    counts = {'s':0, 'n':0}
    for entry, target, row, offset, thresholds, activity, count, bounds, values in (
            (0xC1C8, 0xC1D8, 0x7217, 0x71B9, 0x95F0, 0x988E, 30, 0x964E, 0x988E),
            (0xC1EC, 0xC1FC, 0x73D8, 0x737D, 0x98F6, 0x9632, 14, 0x9690, 0x98F6)):
        for prefix in prefixes:
            index = ((int(prefix)-1)&65535) if prefix else 36
            low_index = index & 255
            for symbol in 'sn':
                for pattern in range(5):
                    memory.banks = [bank.copy() for bank in original_banks]
                    memory.memory = [None, memory.banks[5], memory.banks[2], None]
                    memory.out7ffd(0x16)
                    memory[0x6306] = 0x16
                    memory[row], memory[offset] = 29, 7
                    put(memory, 0x7FFE, bytes((255, 63)))
                    variant = (0, 1, 255, 0, 1)[pattern]
                    put(memory, 0x983F, bytes((0x38, 0x4B, 0x57, 0x13, variant)))
                    persistent = [(0xC804, target&255), (0xC805, target>>8)]
                    if symbol == 's':
                        size = signature(0x4B38, 0x1357, variant)['size']
                        # Создание пяти профилей активности, равенства и первого либо последнего отказа.
                        for i in range(count):
                            memory[thresholds+2*i] = size if pattern == 2 else size+1
                            memory[activity+i] = 0 if pattern == 0 else 255 if pattern == 1 else 1
                            if pattern == 4 and i != count-1:
                                memory[activity+i] = 0
                        failure = next((i for i in range(count) if memory[activity+i] not in (0, 255)
                                        and size < memory[thresholds+2*i]), None)
                        result = int(failure is None)
                        out_hl = thresholds+2*(count if failure is None else failure)
                        out_b = 0 if failure is None else count-failure
                        out_c, out_a = 36, result
                        last = count-1 if failure is None else failure
                        flags = (0x44 if failure is None and memory[activity+last] in (0, 255)
                                 else compare_flags(size, memory[thresholds+2*last]))
                        # Расчёт всей независимой последовательности рабочего ключа.
                        persistent.append((0x6306, 0x11))
                        u, v = 0x4B38, 0x1357
                        def key_writes(u, v):
                            data = u.to_bytes(2, 'little')+v.to_bytes(2, 'little')
                            return [(0x631C+i, value) for i, value in enumerate(data)]
                        persistent += key_writes(u, v)
                        for iteration in range(variant+1):
                            u, v, _ = step_key(u, v)
                            persistent += key_writes(u, v)
                        persistent.extend(((0x6306, 0x10), (0x6306, 0x16), (0xC509, size)))
                        ports = [(0x7FFD, 0x11), (0x7FFD, 0x10), (0x7FFD, 0x16)]
                    else:
                        selected = values+low_index
                        # Создание границ и неактивных FF либо 00 с левым или правым свидетелем.
                        for address in range(selected-2, selected+3):
                            memory[address] = 255 if pattern == 0 else 0
                        pair = bounds+((2*low_index)&255)
                        memory[pair], memory[pair+1] = (0, 0) if pattern == 4 else (254, 2)
                        if pattern == 1:
                            memory[selected-1] = 128
                        elif pattern == 2:
                            memory[selected+1] = 1
                        elif pattern == 3:
                            memory[selected-2] = 254
                        out_a, flags, out_hl, out_c, result = neighbor_reference(memory, low_index, bounds, values)
                        out_b = bounds >> 8
                        ports = []
                    text = prefix+b'.'+symbol.encode()+b'!\r'
                    put(memory, 0xB000, text)
                    cpu.registers[:] = initial
                    r = cpu.registers
                    trace = PortTrace(cpu)
                    cpu.set_tracer(trace)
                    if with_expression_wrappers:
                        persistent.extend(((0xB800, result), (0xB801, 0)))
                    memory.cpu_writes.clear()
                    memory.recording = True
                    cpu.run(start=entry-6 if with_expression_wrappers else entry, stop=0x3FFF)
                    memory.recording = False
                    # Проверка реальных выходов каждого обработчика без обещания общего BC либо F.
                    assert (256*r[6]+r[7], 256*r[4]+r[5], r[2], r[3], r[0], r[1]) == (
                        out_hl, result, out_b, out_c, out_a, flags), (entry, prefix, symbol, pattern, list(r))
                    assert r[12] == 0x8000 and 256*r[8]+r[9] == 0xB000+len(prefix)+2
                    assert r[10:12] == initial[10:12] and r[18] == 2 and r[19] == initial[19]
                    assert r[16:18] == ([0x16, logical_flags(0x16)] if symbol == 's' else initial[16:18])
                    if with_expression_wrappers:
                        assert (256*r[20]+r[21], 256*r[22]+r[23]) == (result, 0xB802)
                        assert bytes(memory[0x7FFC:0x7FFE]) == bytes((result, 0))
                    else:
                        assert r[20:24] == initial[20:24]
                    lower = 0x7FEE if with_expression_wrappers else 0x7FF0
                    assert [(a,v) for a,v in memory.cpu_writes if not lower <= a < 0x7FFE] == persistent
                    assert bytes(memory[0x7FFE:0x8000]) == bytes((255, 63))
                    assert trace.writes == ports and memory[0x6306] == 0x16 and memory.o7ffd == 0x16
                    counts[symbol] += 1
    result = dict(passed=True, method='original_quantity_suffixes_with_real_banks_and_expression_wrappers',
        cases=sum(counts.values()), cases_by_suffix=counts, expression_wrappers_executed=with_expression_wrappers,
        all_low_index_bytes=True, main_registers_selected_alternatives_flags_and_non_stack_writes_checked=True,
        physical_disk_and_sector_hashes_checked=True, CPU_write_watch_positive_control=True,
        original_return_word_preserved=True, full_R_proved=False,
        all_keys_bounds_values_addresses_and_invalid_suffixes_checked=False,
        stack_bus_cycle_order_verified=False, irq_executed=False, native_execution=False, assembly_executed=False)
    name = 'QuantitySuffixExpressionWrappersVerification.json' if with_expression_wrappers else 'QuantitySuffixesVerification.json'
    (ROOT/'Tools/Disasm/Reports'/name).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main('--expression-wrappers' in sys.argv)
