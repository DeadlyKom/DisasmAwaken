"""Фактические первые инструкции планировщика после записи в 7B60."""
from collections import Counter
import json

from CheckActionMissileConsume import dec_flags
from CheckActionOverlappingKeyClipReturns import run_to
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionRecordSearch import inc_flags
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put


def main():
    flat = flat_action()
    assert flat[0x7B58:0x7B66] == [0x3E, 0x80, 0x0F, 0x32, 0x59, 0x7B, 0xD0, 0, 0x3E, 0, 0x3D, 0xF2, 0xA8, 0x79]
    banks = [bytearray(16384) for _ in range(8)]
    for page, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[page][:] = flat[address:address + 16384]
    memory = RecordedBanks(banks=banks, out7ffd=0x10)
    simulator = Simulator(memory)
    put(memory, 0xBFFE, (255, 63))
    compared = (*range(13), 14, *range(16, 25), 26, 27)
    counts = Counter()
    routes = Counter()

    for opcode in (*range(1, 8), 0xC9, 0x3E):
        for phase in range(1, 256, 2):
            for counter in range(256):
                memory.recording = False
                memory[0x7B59], memory[0x7B60], memory[0x7B61] = phase, opcode, counter
                scratch = 0x9100 + counter
                if opcode == 2:
                    memory[scratch] = 0xA5
                bc = scratch if opcode == 2 else ((phase * 73 + counter) & 255) << 8 | counter
                flags = (phase * 41 + counter * 73) & 255
                registers = get_registers({'PC': 0x7B58, 'SP': 0xBFFE, 'AF': 0x5A00 | flags, 'BC': bc,
                                           'HL': 0x2468, 'DE': 0x1357, 'IX': 0x4567, 'IY': 0xCDEF}, None, False)
                simulator.registers[:] = registers
                wanted = list(registers)
                rotated = (phase >> 1) | 128
                wanted[:2] = [rotated, (flags & 0xC4) | (rotated & 0x28) | 1]
                wanted[PC] = 0x7B60
                writes = [(5, 0x3B59, rotated)]
                memory.writes = []
                memory.recording = True
                run_to(simulator, 0x7B60, 10)
                assert all(simulator.registers[index] == wanted[index] for index in compared)

                # Эффект именно изменённого первого опкода, байт 7B61 подаётся во всех значениях.
                wanted[PC] = 0x7B61
                if opcode == 1:
                    wanted[2:4] = [0x3D, counter]
                    wanted[PC] = 0x7B63
                elif opcode == 2:
                    writes.append((2, scratch - 0x8000, rotated))
                elif opcode == 3:
                    word = (bc + 1) & 65535
                    wanted[2:4] = [word >> 8, word & 255]
                elif opcode == 4:
                    wanted[2], wanted[1] = (wanted[2] + 1) & 255, inc_flags(wanted[2], 1)
                elif opcode == 5:
                    wanted[2], wanted[1] = (wanted[2] - 1) & 255, dec_flags(wanted[2], 1)
                elif opcode == 6:
                    wanted[2], wanted[PC] = counter, 0x7B62
                elif opcode == 7:
                    wanted[:2] = [phase, (wanted[1] & 0xC4) | (phase & 0x28) | 1]
                elif opcode == 0xC9:
                    wanted[PC], wanted[SP] = 0x3FFF, 0xC000
                else:
                    wanted[0], wanted[PC] = counter, 0x7B62
                simulator.run()
                assert all(simulator.registers[index] == wanted[index] for index in compared), (opcode, phase, counter)
                assert memory.writes == writes and memory.o7ffd == 0x10
                counts[f'{opcode:02X}'] += 1

                # При исходном нулевом счётчике ветвь до следующего входа остаётся ограниченной.
                if counter == 0 and opcode != 0xC9:
                    if wanted[PC] == 0x7B61:
                        simulator.run()
                        wanted[PC] += 1
                    if wanted[PC] == 0x7B62:
                        simulator.run()
                        wanted[1] = dec_flags(wanted[0], wanted[1] & 1)
                        wanted[0] = (wanted[0] - 1) & 255
                    wanted[PC] = 0x7B66 if wanted[1] & 128 else 0x79A8
                    simulator.run()
                    assert all(simulator.registers[index] == wanted[index] for index in compared)
                    assert memory.writes == writes
                    routes[(f'{opcode:02X}', f'{wanted[PC]:04X}')] += 1

    memory.recording = False
    for phase in range(0, 256, 2):
        memory[0x7B59], memory[0x7B60] = phase, 0xC9
        simulator.registers[:] = get_registers({'PC': 0x7B58, 'SP': 0xBFFE}, None, False)
        assert 0x7B60 not in run_to(simulator, 0x3FFF, 10)
        assert memory[0x7B59] == phase >> 1

    assert counts.total() == 9 * 128 * 256
    result = dict(passed=True, total_cases=counts.total() + 128, opcode_profiles=dict(counts),
                  all_admitted_phase_bytes_and_counter_bytes=True, blocked_phase_profiles=128,
                  original_counter_zero_routes={':'.join(key): count for key, count in routes.items()},
                  exact_registers_except_R_T_and_ordered_writes=True,
                  successor_algorithms_executed=False, full_mutable_counter_stream_proved=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionPatchedScheduleGateVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
