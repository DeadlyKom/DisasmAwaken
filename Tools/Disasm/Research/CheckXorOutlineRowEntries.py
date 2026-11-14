"""Все внутренние BytesNN, флаги CPL/INC L, точный R и двусловный стек.

Документация: ../../../Docs/XorOutline.md#внутренние-входы-горизонтальной-развёртки
"""
from hashlib import sha256
import json
from CheckGeometryReturnEntries import ROOT, Simulator, get_registers, Memory


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(x for x in manifest['entries'] if x['slot'] == 4)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    assert len(source) == entry['allocated_length']
    assert disk[entry['offset']:entry['offset'] + len(source)] == source
    memory = Memory(65536)
    memory[0x6000:0x6000 + len(source)] = source
    original = bytes(memory[0xC566:0xC5F2])
    expected_code = bytes.fromhex('e53e209387873270c51800') + bytes.fromhex('7e2f772c') * 31 + bytes.fromhex('7e2f77e1c9')
    assert original == expected_code
    # Проверка наблюдателя самостоятельной записью CPU в отдельную память.
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex('320070')
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.writes == [(0x7000, 0)]
    cpu = Simulator(memory)
    initial = get_registers({'HL':0x4000, 'DE':0x12F3, 'BC':0x36C9, 'AF':0x47AD,
        '^HL':0x5678, '^DE':0x6789, '^BC':0x789A, '^AF':0x89AB,
        'IX':0x9ABC, 'IY':0xABCD, 'SP':0x7FFC}, None, False)
    entries = []
    for width in range(1, 33):
        address = 0xC571 + 4 * (32 - width)
        baseline = bytes((i * 73 + width * 7) & 255 for i in range(256))
        refresh_values, flags_values = set(), set()
        cases = 0
        for low in range(256):
            for flags_code in range(16):
                preserved = ((flags_code & 8) << 4) | ((flags_code & 4) << 4) | ((flags_code & 2) << 1) | (flags_code & 1)
                flags = preserved | ((low ^ width) & 0x3A)
                refresh = (low + 17 * flags_code + width) & 255
                refresh_values.add(refresh)
                flags_values.add(flags)
                saved_hl = (((low << 8) | ((flags_code * 17 + width) & 255)) ^ 0xA55A)
                frame = saved_hl.to_bytes(2, 'little') + bytes.fromhex('ff3f')
                memory[0x4000:0x4100] = baseline
                memory[0x7FFC:0x8000] = frame
                memory[0xC570] = 0xAB
                expected = list(initial)
                expected[0], expected[1] = low ^ flags, flags
                expected[6], expected[7] = 0x40, low
                expected[14], expected[15] = width, refresh
                expected[26], expected[27] = flags_code & 1, width % 3
                expected[24] = address
                cpu.registers[:] = expected
                memory.writes.clear()
                memory.recording = True
                cpu.run(address, 0x3FFF)
                memory.recording = False
                # Расчёт исходной байтовой адресации, INC L не переносит переполнение в H.
                addresses = [0x4000 | ((low + i) & 255) for i in range(width)]
                writes = [(p, baseline[p & 255] ^ 255) for p in addresses]
                last_low = addresses[-1] & 255
                value = writes[-1][1]
                if width == 1:
                    result_f = (flags & 0xC5) | (value & 0x28) | 0x12
                else:
                    result_f = ((last_low & 0x80) | (0x40 if last_low == 0 else 0)
                        | (4 if last_low == 0x80 else 0) | (flags & 1) | (value & 0x28) | 0x12)
                expected[0], expected[1] = value, result_f
                expected[6], expected[7] = saved_hl >> 8, saved_hl & 255
                expected[12], expected[24] = 0x8000, 0x3FFF
                expected[15] = (refresh & 0x80) | ((refresh + 4 * width + 1) & 0x7F)
                assert all(cpu.registers[i] == expected[i] for i in range(len(expected)) if i != 25), (width, low, flags)
                assert memory.writes == writes, (width, low, flags, memory.writes, writes)
                target = bytearray(baseline)
                for p, byte in writes: target[p & 255] = byte
                assert memory[0x4000:0x4100] == target
                assert bytes(memory[0x7FFC:0x8000]) == frame and memory[0xC570] == 0xAB
                cases += 1
        assert refresh_values == set(range(256)) and flags_values == set(range(256))
        entries.append(dict(name=f'Bytes{width:02d}', address=address, width=width, cases=cases,
                            M1=4 * width + 1, SP_delta=4))
    report = dict(passed=True, method='all_original_unrolled_XOR_row_entries_against_byte_page_and_explicit_stack',
        cases=sum(x['cases'] for x in entries), entries=entries,
        original_disk_sha256=sha256(disk).hexdigest(), original_row_sha256=sha256(original).hexdigest(),
        all_widths_and_L_bytes_and_16_preserved_flag_combinations=True,
        all_input_F_values_covered_per_width=True, all_initial_R_values_covered_per_width=True,
        complete_L_F_R_joint_product=False, exact_registers_except_T_checked=True,
        every_CPU_RAM_write_value_and_order_checked=True, frame_unchanged=True,
        HorizontalSkip_not_read_or_written_by_inner_entries=True, E_not_used_for_inner_byte_count=True,
        R_bit7_preserved=True, CPU_write_watch_positive_control=True,
        no_own_stack_writes=True, destination_page_fixed_to_4000=True,
        all_saved_HL_values_or_stack_addresses_or_overlaps_checked=False,
        normal_driver_entry_not_executed=True, IRQ_or_native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/XorOutlineRowEntriesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('passed', 'cases', 'all_input_F_values_covered_per_width')}))


if __name__ == '__main__':
    main()
