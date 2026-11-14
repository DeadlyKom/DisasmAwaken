"""State07 и State11 с полным общим хвостом либо реальным освобождением.

Документация: ../../../Docs/ActionTimedDecayState.md#полный-вызов-и-повторный-инкремент
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionTimedDecayState import reference as decay_reference
from CheckActionTimedPhaseState import reference as phase_reference
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from CheckStationFlightCycle import payload


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    cpu = Simulator(memory)
    touched = set()
    paths = Counter()
    witnesses = {}
    cases = 0
    for entry in (0xF66A, 0xF3A1):
        for value in range(256):
            for timer in (0, 1, 2, 255):
                for cls in (3, 20):
                    for marker in (False, True):
                        for carry in (0, 1):
                            for limit in (0, 3, 255):
                                memory.recording = False
                                for bank, offset in touched:
                                    memory.banks[bank][offset] = baseline[bank][offset]
                                ix = 0xA100 + 64 * (cases % 16)
                                stack = (0x9008, 0xBFFE)[cases & 1]
                                record = {1: 128 if marker else 127, 7: value * 109 & 255,
                                    8: value, 9: (value * 73 + timer) & 255, 10: 7 if entry == 0xF66A else 17,
                                    15: limit, 16: value if entry == 0xF66A else (value * 31 + timer) & 255,
                                    17: timer if entry == 0xF66A else 9, 18: cls, 22: 2,
                                    23: timer if entry == 0xF3A1 else 9, 24: 0, 36: 128}
                                for offset, byte in record.items():
                                    memory[ix + offset] = byte
                                memory[stack], memory[stack + 1] = 255, 63
                                initial = get_registers({'PC': entry, 'SP': stack, 'AF': (cases & 0xFFFE) | carry,
                                    'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0,
                                    '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, 'IX': ix, 'IY': 0x5C3A}, None, False)
                                initial[14], initial[15], initial[26], initial[27] = cases & 255, cases * 73 & 255, cases & 1, cases % 3
                                expected = [bytearray(b) for b in memory.banks]
                                expected_writes = []

                                def apply(writes, update=False):
                                    for address, byte in writes:
                                        bank = 5 if address < 0x8000 else 2 if address < 0xC000 else 0
                                        expected[bank][address & 0x3FFF] = byte
                                        expected_writes.append((bank, address & 0x3FFF, byte))
                                        if update and ix <= address < ix + 64:
                                            record[address - ix] = byte

                                # Независимый префикс задаёт состояние до общего хвоста.
                                reference = decay_reference if entry == 0xF66A else phase_reference
                                wanted, writes, own_path = reference(initial, record, ix)
                                prefix_AF_prime = wanted[16] * 256 + wanted[17]
                                apply(writes, update=True)
                                common_path = 'direct_return'
                                if wanted[24] != 0x3FFF:
                                    assert wanted[24] == 0xF0F8
                                    wanted, writes, common_path = prepare_reference(wanted, ix, record)
                                    apply(writes)
                                    if wanted[24] == 0x6D06:
                                        view = RecordedBanks(banks=expected, out7ffd=16)
                                        result = vector_reference(view, wanted, (record[7], (record[8] + 128) & 255, record[9]), 0x3FFF)
                                        wanted = result['registers']
                                        apply(result['writes'])
                                cpu.registers[:] = initial
                                ports = PortTrace(cpu)
                                cpu.set_tracer(ports)
                                memory.writes = []
                                memory.recording = True
                                cpu.run(start=entry, stop=0x3FFF)
                                memory.recording = False
                                compared = (*range(25), 26, 27)
                                assert all(cpu.registers[i] == wanted[i] for i in compared), (entry, value, timer, cls, marker, carry, limit, 'registers')
                                assert memory.banks == expected and Counter(memory.writes) == Counter(expected_writes), (entry, value, timer, 'RAM')
                                assert not ports.writes and memory.o7ffd == 16
                                # Наглядные свидетели общего инкремента и замены альтернативного AF.
                                if cls == 3 and carry == 0 and limit == 3 and timer == 2:
                                    if entry == 0xF66A and value in (0, 1, 2) and not marker:
                                        witnesses['decay_' + str(value)] = dict(scale_in=value, scale_before_common=record[16],
                                            scale_out=memory[ix + 16], final_AF=cpu.registers[0] * 256 + cpu.registers[1])
                                    if entry == 0xF3A1 and value == 28:
                                        witnesses['pattern_marker' if marker else 'pattern_active'] = dict(
                                            prefix_AF_prime=prefix_AF_prime,
                                            final_AF_prime=cpu.registers[16] * 256 + cpu.registers[17],
                                            final_AF=cpu.registers[0] * 256 + cpu.registers[1])
                                touched = {(bank, offset) for bank, offset, _ in expected_writes}
                                touched.update((2, (ix + offset) & 0x3FFF) for offset in record)
                                touched.update((2, (stack + i) & 0x3FFF) for i in (0, 1))
                                paths[f'{entry:04X}/{own_path}/{common_path}'] += 1
                                cases += 1
    assert cases == 49152
    assert [witnesses['decay_' + str(v)]['scale_out'] for v in (0, 1, 2)] == [1, 1, 2]
    assert witnesses['pattern_active']['final_AF_prime'] != witnesses['pattern_active']['prefix_AF_prime']
    assert witnesses['pattern_marker']['final_AF_prime'] == witnesses['pattern_marker']['prefix_AF_prime']
    result = dict(passed=True, original_action_sha256=sha256(payload(17)).hexdigest(),
        total_cases=cases, paths=dict(paths), witnesses=witnesses,
        full_external_return=True, actual_mark_reuse_and_common_tail_children=True,
        exact_registers_including_R=True, all_eight_banks_and_write_multiplicity=True,
        all_scale_bytes_for_decay=True, all_phase1_bytes_for_pattern=True,
        timer_samples=[0, 1, 2, 255], class_samples=[3, 20], marker_and_active=True,
        both_input_carries=True, limit_samples=[0, 3, 255], initial_high_scale=128,
        correlated_pattern_phase2_and_low_scale=True, all_input_products_exhausted=False,
        no_OUT=True, exact_T_claimed=False, irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionTimedOffsetsCompositionVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
