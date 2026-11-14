"""Возвраты C0C9 с клавиатурной рамкой, координатами и всеми байтами размера.

Документация: ../../../Docs/ActionKeyDispatchPrefix.md#байтовый-размер-скрытого-отсечения
"""
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
    zero_size_paths = Counter()
    size_counts = Counter()
    appended_pairs = Counter()
    wrap_cases = 0
    examples = {}
    positions = product((0, 127, 255), (0, 47, 95), (-256, -64, -1), (-256, -64, -1), (0, 8, 15), (0, 1))
    profiles = [(*position, 0) for position in positions]
    # Проверка всех ненулевых размеров на представителях трёх путей, отметок и запрета углов.
    profiles.extend((*point, seen, block, size)
                    for point, seen, block, size in product(
                        ((0,0,-256,-256), (127,0,-256,-256)), (0,8,15), (0,1), range(1,256)))
    for second0, first0, second1, first1, seen, block, initial_size in profiles:
        memory.recording = False
        for bank, original in zip(memory.banks, baseline):
            bank[:] = original
        put(memory, 0xCF0B, packed_point(second0, first0, 0xF0))
        put(memory, 0xCF1B, packed_point(second1, first1, 0x5A))
        memory[0xCF07] = seen
        memory[0xCF03] = block
        memory[0x9BA3] = initial_size
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
        # Проверка адресов выходных пар отдельно от полного сравнения числовой композиции.
        output_writes = [(offset,value) for bank,offset,value in memory.writes if bank == 2 and 0x1000 <= offset < 0x1100]
        pairs = len(output_writes) // 2
        assert pairs in (1,2) and len(output_writes) == 2 * pairs
        assert [offset for offset,value in output_writes] == [0x1000 + ((initial_size + i) & 255) for i in range(2 * pairs)]
        final_size = memory[0x9BA3]
        assert final_size == (initial_size + 2 * pairs) & 255
        size_counts[initial_size] += 1
        appended_pairs[pairs] += 1
        wrap_cases += int(initial_size + 2 * pairs >= 256)

        return_sp = simulator.registers[SP]
        assert return_sp == 0xBFF6 and 0xC993 not in visited and 0xC6EA not in visited
        run_to(simulator, 0x6F55, 20)
        assert simulator.registers[SP] == 0xBFFE
        paths = [name for entry, name in path_entries.items() if entry in visited]
        assert len(paths) == 1, paths
        path = paths[0]
        assert not ports.outs and memory.o7ffd == 16
        counts[path] += 1
        if initial_size == 0:
            zero_size_paths[path] += 1
        examples.setdefault(path, dict(points=[[second0, first0], [second1, first1]], seen=seen, block=block,
                                      immediate_return=immediate_return, sp_after_clip=return_sp,
                                      final_PC=simulator.registers[PC]))
    assert set(counts) == set(path_entries.values()) and counts.total() == 3546, counts
    assert set(size_counts) == set(range(256))
    result = dict(passed=True, total_cases=counts.total(), paths=dict(counts), examples=examples,
                  real_keyboard_scan_first_handler_clip_and_return_executed=True,
                  prepared_valid_clip_coordinates=True, geometry_initialized_by_game_before_key_not_proved=True,
                  exact_registers_except_R_T_all_banks_and_write_multiplicity_compared_at_clip_return=True,
                  original_keyboard_frame_used_without_substitution=True,
                  all_three_abstract_paths_end_in_normal_RET=True, geometry_finish_C993_bypassed=True,
                  RestoreKeyScanFrame_returns_to_decay_with_original_SP=True,
                  stopped_before_decay=True, author_intent_proved=False,
                  original_zero_size_cases=486, all_initial_output_size_bytes_checked=True,
                  zero_size_paths=dict(zero_size_paths),
                  size_cases=dict(sorted(size_counts.items())), appended_pair_counts=dict(appended_pairs),
                  output_wrap_cases=wrap_cases, output_writes_stay_in_page_90=True,
                  odd_size_natural_reachability_proved=False,
                  assembly_executed=False, native_execution=False)
    report = reports / 'ActionOverlappingKeyClipReturnsVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
