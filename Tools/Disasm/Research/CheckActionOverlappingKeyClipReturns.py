"""Возвраты C0C9 с реальной клавиатурной рамкой и подготовленными координатами отсечения."""
from collections import Counter
from itertools import product
import json
import sys

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionOverlappingKeyDispatch import StationaryKey
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put
from ReferenceActionClipping import Clipping

sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from InspectZ80 import decoder


def packed_point(second, first, code):
    coordinates = (second & 65535).to_bytes(2, 'little') + (first & 65535).to_bytes(2, 'little')
    return coordinates + bytes((code,))


def run_to(simulator, target, limit):
    visited = set()
    for _ in range(limit):
        if simulator.registers[PC] == target:
            return visited
        visited.add(simulator.registers[PC])
        simulator.run()
    raise AssertionError(('граница не достигнута', hex(target), hex(simulator.registers[PC])))


def main():
    flat = flat_action()
    baseline = [bytearray([160 + page] * 16384) for page in range(8)]
    for page, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[page][:] = bytes(flat[start:start + 16384])
    memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
    simulator = Simulator(memory)
    ports = StationaryKey()
    simulator.set_tracer(ports)
    operations = {
        item.address: dict(operation=item.operation, hex=item.bytes.hex())
        for item in decoder(flat).disassemble(0xC07A, 0xC477, 'h')
    }
    reports = ROOT / 'Tools/Disasm/Reports'
    decisions = json.loads((reports / 'ActionClipDecisionPaths.json').read_bytes())['cases']
    case = next(row for row in decisions if row['entry'] == 0xC0C9)
    assert len(case['paths']) == 3 and {path['exit'] for path in case['paths']} == {'normal'}
    path_entries = {0xC4F6: 'top_intersection', 0xC641: 'left_then_corner_request', 0xC0E0: 'left_then_corner_mark'}
    counts = Counter()
    examples = {}
    positions = product((0, 127, 255), (0, 47, 95), (-256, -64, -1), (-256, -64, -1), (0, 8, 15), (0, 1))
    for second0, first0, second1, first1, seen, block in positions:
        memory.recording = False
        for bank, original in zip(memory.banks, baseline):
            bank[:] = original
        put(memory, 0xCF0B, packed_point(second0, first0, 0xF0))
        put(memory, 0xCF1B, packed_point(second1, first1, 0x5A))
        memory[0xCF07] = seen
        memory[0xCF03] = block
        memory[0x9BA3] = 0
        put(memory, 0xBFFE, (255, 63))
        simulator.registers[:] = get_registers({'PC': 0x6F1D, 'SP': 0xBFFE, 'HL': 0x1357}, None, False)
        ports.reads.clear()
        ports.outs.clear()
        run_to(simulator, 0xC0C9, 1000)
        assert len(ports.reads) == 27
        assert bytes(memory[0xBFF4:0xBFFE]) == bytes.fromhex('4e6f 829d fefd 4b70 0113')

        # Проверка числовой композиции с фактическими словами клавиатурной рамки.
        immediate_return = 0x6F4E
        oracle = Clipping(memory.banks, simulator.registers, operations, PC, SP)
        oracle.run(stop=immediate_return)
        assert not oracle.special
        memory.writes = []
        memory.recording = True
        visited = run_to(simulator, immediate_return, 3000)
        memory.recording = False
        compared = (*range(13), 14, *range(16, 25), 26, 27)
        assert all(oracle.r[index] == simulator.registers[index] for index in compared)
        assert memory.banks == oracle.banks and Counter(memory.writes) == Counter(oracle.writes)

        return_sp = simulator.registers[SP]
        assert return_sp == 0xBFF6 and 0xC993 not in visited and 0xC6EA not in visited
        run_to(simulator, 0x6F55, 20)
        assert simulator.registers[SP] == 0xBFFE
        paths = [name for entry, name in path_entries.items() if entry in visited]
        assert len(paths) == 1, paths
        path = paths[0]
        assert not ports.outs and memory.o7ffd == 16
        counts[path] += 1
        examples.setdefault(path, dict(points=[[second0, first0], [second1, first1]], seen=seen, block=block,
                                      immediate_return=immediate_return, sp_after_clip=return_sp,
                                      final_PC=simulator.registers[PC]))
    assert set(counts) == set(path_entries.values()) and counts.total() == 486, counts
    result = dict(passed=True, total_cases=counts.total(), paths=dict(counts), examples=examples,
                  real_keyboard_scan_first_handler_clip_and_return_executed=True,
                  prepared_valid_clip_coordinates=True, geometry_initialized_by_game_before_key_not_proved=True,
                  exact_registers_except_R_T_all_banks_and_write_multiplicity_compared_at_clip_return=True,
                  original_keyboard_frame_used_without_substitution=True,
                  all_three_abstract_paths_end_in_normal_RET=True, geometry_finish_C993_bypassed=True,
                  RestoreKeyScanFrame_returns_to_decay_with_original_SP=True,
                  stopped_before_decay=True, author_intent_proved=False,
                  assembly_executed=False, native_execution=False)
    report = reports / 'ActionOverlappingKeyClipReturnsVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
