"""E97C до внешнего RET, поиск класса 8 и полный вычислитель смещений.

Документация: ../../../Docs/ActionSelectClass8.md#полный-внешний-возврат
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionRecordIndex import decode
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from ReferenceControlsPointRespawn import refresh
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from CheckStationFlightCycle import payload


def prefix(initial, memory):
    """Независимый поиск по данным списка, без исполнения инструкций Z80."""
    r = list(initial)
    stack, ix = r[12], r[8] * 256 + r[9]
    r[4], r[2:4] = 8, [0, 64]
    writes = []

    def word(address, value):
        writes.extend(((address, value & 255), (address + 1, value >> 8)))

    word(stack - 2, 0xE981)
    cursor, found, m1 = 0xA100, False, 3
    # Поиск первого активного полного класса 08 до терминального маркера.
    while True:
        word(stack - 4, 0xE997)
        m1 += 2
        while True:
            m1 += 6
            if memory[cursor + 1] != 128:
                break
            m1 += 4
            if memory[cursor] == 128:
                m1 += 1
                break
            cursor += 64
        if memory[cursor + 1] == 128 and memory[cursor] == 128:
            break
        m1 += 4
        if memory[cursor + 18] == 8:
            m1 += 2
            found = True
            break
        cursor += 64
    r[10:12] = [cursor >> 8, cursor & 255]
    if found:
        index, flags, _ = decode(cursor)
        r[0:2] = [index, flags]
        word(stack - 2, 0xE987)
        word(stack - 4, initial[6] * 256 + initial[7])
        word(stack - 6, cursor)
        word(stack - 6, 0xE6C5)
        writes.append((ix + 32, index))
        m1 += 23
    else:
        r[0:2] = [128, 0x42]
        m1 += 3
    r[15], r[24] = refresh(r[15], m1), 0xF0F8
    return r, writes, found, cursor


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    cpu, touched, paths, witnesses = Simulator(memory), set(), Counter(), {}
    cases = 0
    for position in range(26):
        for code in range(256):
            for marker in (False, True):
                memory.recording = False
                for bank, offset in touched:
                    memory.banks[bank][offset] = baseline[bank][offset]
                setup = {}
                # Создание списка с единственной проверяемой записью и отдельным терминатором.
                for index in range(25):
                    address = 0xA100 + 64 * index
                    setup.update({address: 0, address + 1: 128, address + 18: 254})
                if position < 25:
                    address = 0xA100 + 64 * position
                    setup.update({address: position, address + 1: 1, address + 18: code})
                setup.update({0xA740: 128, 0xA741: 128})
                # Текущая запись не принадлежит поисковому списку, её маркер независим от результата поиска.
                ix, stack = 0xA800, (0x9008, 0xBFFE)[code & 1]
                record = {1: 128 if marker else 127, 7: code * 109 & 255, 8: code,
                    9: (code * 73 + position) & 255, 10: 0x13 if (code ^ position) & 4 else 2,
                    15: (0, 3, 127, 255)[(code + position) & 3], 16: code, 18: 3 if (code ^ position) & 8 else 20,
                    32: (code + 137) & 255, 33: (code * 73 + 85) & 255,
                    36: (0, 1, 128, 255)[position & 3]}
                setup.update({ix + offset: byte for offset, byte in record.items()})
                setup.update({stack: 255, stack + 1: 63})
                for address, byte in setup.items():
                    memory[address] = byte
                initial = get_registers({'PC': 0xE97C, 'SP': stack, 'AF': cases & 65535,
                    'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0,
                    '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, 'IX': ix, 'IY': 0x5C3A}, None, False)
                initial[14], initial[15], initial[26], initial[27] = code, cases * 73 & 255, cases & 1, cases % 3
                expected = [bytearray(b) for b in memory.banks]
                expected_writes = []

                def apply(writes):
                    for address, byte in writes:
                        bank = 5 if address < 0x8000 else 2 if address < 0xC000 else 0
                        expected[bank][address & 0x3FFF] = byte
                        expected_writes.append((bank, address & 0x3FFF, byte))

                # Расчёт префикса, общего подготовителя и полного числового вычислителя.
                wanted, writes, found, selected = prefix(initial, memory)
                apply(writes)
                prefix_iy = wanted[10] * 256 + wanted[11]
                wanted, writes, path = prepare_reference(wanted, ix, record)
                apply(writes)
                if not marker:
                    result = vector_reference(RecordedBanks(banks=expected, out7ffd=16), wanted,
                        (record[7], (record[8] + 128) & 255, record[9]), 0x3FFF)
                    wanted = result['registers']
                    apply(result['writes'])
                cpu.registers[:] = initial
                ports = PortTrace(cpu)
                cpu.set_tracer(ports)
                memory.writes, memory.recording = [], True
                cpu.run(start=0xE97C, stop=0x3FFF)
                memory.recording = False
                # Проверка полного контекста, всех банков и кратности присваиваний CPU.
                compared = (*range(25), 26, 27)
                assert all(cpu.registers[i] == wanted[i] for i in compared), (position, code, marker, 'registers',
                    [(i, wanted[i], cpu.registers[i]) for i in compared if wanted[i] != cpu.registers[i]])
                assert memory.banks == expected and Counter(memory.writes) == Counter(expected_writes), (position, code, marker, 'RAM')
                assert not ports.writes and memory.o7ffd == 16
                assert memory[ix + 32] == (position if found else record[32])
                assert memory[ix + 33] == record[33]
                if position == 12 and code == 8:
                    witnesses['marker' if marker else 'active'] = dict(found=found, selected=selected,
                        prefix_IY=prefix_iy, final_IY=cpu.registers[10] * 256 + cpu.registers[11],
                        final_AF=cpu.registers[0] * 256 + cpu.registers[1], proximity_index=memory[ix + 32])
                touched = {(bank, offset) for bank, offset, _ in expected_writes}
                touched.update((5 if address < 0x8000 else 2 if address < 0xC000 else 0, address & 0x3FFF) for address in setup)
                paths[f'{"found" if found else "not_found"}/{path}'] += 1
                cases += 1
    assert cases == 13312
    assert all(paths[key] for key in ('found/increment', 'found/preserve', 'found/marker_return'))
    assert witnesses['marker']['final_IY'] == witnesses['marker']['selected']
    assert witnesses['active']['final_IY'] != witnesses['active']['selected']
    result = dict(passed=True, original_action_sha256=sha256(payload(17)).hexdigest(), total_cases=cases,
        paths=dict(paths), witnesses=witnesses, full_external_return=True, actual_search_index_and_common_children=True,
        all_256_candidate_codes_and_26_positions=True, all_low_scale_bytes=True,
        active_and_marker_current_records=True, current_record_outside_search_list=True,
        self_selection_covered_by_separate_prefix_model=True, correlated_phases_limits_classes_states=True,
        high_scale_samples=[0, 1, 128, 255], exact_registers_including_R=True,
        all_eight_banks_and_write_multiplicity=True, no_OUT=True,
        all_input_products_exhausted=False, exact_T_claimed=False,
        irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionSelectClass8CompositionVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
