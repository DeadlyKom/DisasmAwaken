"""F0F8 до внешнего RET вместе с коэффициентами и тремя настоящими умножениями.

Документация: ../../../Docs/ActionObjectOffsetTransfer.md#полный-выход-через-вычислитель
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionObjectOffsetTransfer import reference as prepare
from CheckActionObjectOffsetVector import table_reference, multiply, cost, RESULT_WORDS, COEFFICIENT_OPERANDS
from CheckMusic import Simulator, get_registers
from CheckMusicGateTicks import Memory
from CheckStationFlightCycle import payload
from ReferenceControlsPointRespawn import refresh


def profiles():
    for current in range(256):
        for high in (0, 1, 127, 128, 255):
            for limit in (0, 1, 127, 255):
                for cls, state in ((3, 2), (9, 19), (20, 2)):
                    yield False, current, high, limit, cls, state
    for flags in range(256):
        yield True, flags, flags, flags, 3, 2


def main():
    original = flat_action()
    memory = Memory(original)
    cpu = Simulator(memory)
    touched = set()
    counts = Counter()
    for serial, (marker, current, high, limit, cls, state) in enumerate(profiles()):
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        ix = 0xA100 + 64 * (serial % 16)
        stack = (0x9008, 0xBFFE)[serial & 1]
        record = {1: 128 if marker else 127, 7: current, 8: high * 73 & 255,
            9: current * 109 & 255, 10: state, 15: limit, 16: current, 18: cls, 36: high}
        for offset, value in record.items():
            memory[ix + offset] = value
        memory[stack], memory[stack + 1] = 255, 63
        initial = get_registers({'PC': 0xF0F8, 'SP': stack, 'AF': serial & 65535,
            'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': ix, 'IY': 0x5C3A}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial * 73 & 255, serial & 1, serial % 3
        expected = list(memory)
        wanted, writes, path = prepare(initial, ix, record)
        writes = list(writes)
        for address, value in writes:
            expected[address] = value
        if not marker:
            prefix_r = wanted[15]
            scale = wanted[4] * 256 + wanted[5]
            offsets = (record[7], (record[8] + 128) & 255, record[9])
            wanted, coefficients, m1, overflow = table_reference(expected, wanted, offsets)

            def word(address, value):
                writes.extend(((address, value & 255), (address + 1, value >> 8)))

            # Порядок присваиваний соответствует модели PUSH, не аппаратным шинным циклам.
            word(stack - 2, ix)
            word(stack - 4, scale)
            word(stack - 6, 0x6D0C)
            writes.extend(zip(COEFFICIENT_OPERANDS, coefficients))
            word(stack - 4, scale)
            for index, (address, coefficient) in enumerate(zip(RESULT_WORDS, coefficients)):
                result, count = multiply(wanted, coefficient, scale)
                word(address, result)
                m1 += count
                if index == 0:
                    word(stack - 4, scale)
            wanted[8:10] = initial[8:10]
            wanted[12], wanted[15], wanted[24] = stack + 2, refresh(prefix_r, m1 + cost(0x6D06, 0x6D38)), 0x3FFF
        for address, value in writes:
            expected[address] = value
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        cpu.run(start=0xF0F8, stop=0x3FFF)
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(cpu.registers[i] == wanted[i] for i in compared), (serial, path, 'registers')
        assert memory.writes == writes, (serial, path, 'ordered_writes')
        assert memory == expected, (serial, path, 'whole_memory')
        touched = {address for address, _ in writes} | {ix + offset for offset in record} | {stack, stack + 1}
        counts['marker' if marker else f'{cls:02X}/{state:02X}/{path}'] += 1
    assert sum(counts.values()) == 15616
    report = dict(passed=True, original_action_sha256=sha256(payload(17)).hexdigest(),
        total_cases=sum(counts.values()), paths=dict(counts), entry=0xF0F8, stop=0x3FFF,
        complete_external_return=True, real_coefficient_and_three_multiply_children=True,
        exact_registers_including_R=True, all_64K_bytes_and_ordered_assignments=True,
        all_low_scale_bytes=True, high_scale_samples=[0, 1, 127, 128, 255],
        limit_samples=[0, 1, 127, 255], class_state_profiles=[[3, 2], [9, 19], [20, 2]],
        I_IM_IFF_varied_and_preserved=True, stack_locations=[0x9008, 0xBFFE],
        original_tables_used=True, all_input_products_exhausted=False,
        exact_T_claimed=False, irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectOffsetTransferCompositionVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
