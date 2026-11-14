"""Тройки клавиш из подтверждённого входа полётного сканера.

Документация: ../../../Docs/ControlsTemporaryModule.md#тройки-клавиш-в-одном-проходе-сканера
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import comb
import json

from CheckFlightKeyPairs import (ControlSourceMemory, DISK, PairPorts, SnapshotReady,
                                 flat_action, payload)
from TraceFlight import ROOT, PC, SP, H, L, Simulator, main as trace


class ChordMemory(ControlSourceMemory):
    """Наблюдает также согласованное окно фиксированной копии загрузчика."""

    def __init__(self):
        super().__init__()
        self.fixed_module_writes = []

    def __setitem__(self, address, value):
        if self.watch_writes and 0x5DA0 <= address < 0x5EDB:
            self.fixed_module_writes.append((address, value))
        super().__setitem__(address, value)


def main():
    snapshot = {}

    def capture(frame, memory, registers):
        snapshot.update(banks=[bank.copy() for bank in memory.banks],
                        page=memory.o7ffd, registers=list(registers), frame=frame)
        raise SnapshotReady

    try:
        trace(['--frames', '2'], scan_observer=capture, save_reports=False)
    except SnapshotReady:
        pass
    assert snapshot and snapshot['page'] == 0x10
    original = flat_action()
    # Проверка исходного файла и обеих таблиц до формирования синтетических нажатий.
    assert (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes() == payload(17)
    matrix = [tuple(original[p:p + 2]) for p in range(0x9D4C, 0x9D82, 2)]
    targets = [original[p] + 256 * original[p + 1] for p in range(0x7017, 0x704D, 2)]
    keys = list(dict.fromkeys(matrix))
    assert len(keys) == 26 and matrix[0] == matrix[-1]
    cases = []
    dispatch_totals = Counter()
    enabled_iff_positions = Counter()
    for pressed in combinations(keys, 3):
        memory = ChordMemory()
        for destination, saved in zip(memory.banks, snapshot['banks']):
            destination[:] = saved
        memory.out7ffd(snapshot['page'])
        assert [(memory[p], memory[p + 1]) for p in range(0x9D4C, 0x9D82, 2)] == matrix
        assert [memory[p] + 256 * memory[p + 1] for p in range(0x7017, 0x704D, 2)] == targets
        memory.watch_writes = True
        cpu = Simulator(memory)
        cpu.registers[:] = snapshot['registers']
        # Прежний портовый стенд принимает любое число замкнутых пар строки и маски.
        ports = PairPorts(memory, pressed)
        cpu.set_tracer(ports)
        expected = [targets[index] for index, pair in enumerate(matrix) if pair in pressed]
        observed = []
        returns = 0
        temporary_entries = set()
        enabled_iff_steps = 0
        for steps in range(200000):
            pc = cpu.registers[PC]
            bank = memory.o7ffd & 7
            if pc == 0x6F55:
                break
            if cpu.registers[26]:
                enabled_iff_steps += 1
                enabled_iff_positions[bank, pc] += 1
            if pc == 0x6F4D:
                observed.append(cpu.registers[H] * 256 + cpu.registers[L])
            if pc == 0x6F4E:
                returns += 1
            if (bank == 1 and 0xDADE <= pc < 0xDB5D) or 0x5DA0 <= pc < 0x5EDB:
                temporary_entries.add((bank, pc))
            cpu.run()
        else:
            raise AssertionError((pressed, 'scanner did not finish', hex(pc)))
        # Проверка порядка всех вызовов, возвратов и отсутствия изменения исследуемого модуля.
        assert observed == expected, (pressed, observed, expected)
        assert returns == len(expected) and cpu.registers[SP] == snapshot['registers'][SP]
        assert len(ports.reads) == 27
        assert not temporary_entries and not memory.control_writes, (pressed, temporary_entries, memory.control_writes)
        assert not memory.fixed_module_writes, (pressed, memory.fixed_module_writes)
        dispatch_totals.update(observed)
        cases.append(dict(keys=pressed, handlers=observed, instructions=steps,
                          enabled_iff_steps=enabled_iff_steps))
        if len(cases) % 325 == 0:
            print(f'Checked {len(cases)} / {comb(len(keys), 3)} three-key profiles', flush=True)
    # Каждый физический ключ присутствует в C(25,2) тройках, дубли таблицы учитываются отдельно.
    assert len(cases) == comb(26, 3) == 2600
    assert dispatch_totals == Counter({target: count * comb(25, 2) for target, count in Counter(targets).items()})
    report = dict(passed=True, cases=len(cases), profiles=cases,
                  original_TRD_sha256=sha256(DISK).hexdigest(),
                  actual_snapshot_key_and_target_tables_compared=True,
                  matrix_entries=27, distinct_keys=26, pressed_keys_per_profile=3,
                  duplicate_physical_key_dispatches_both_entries=True,
                  snapshot_frame=snapshot['frame'], snapshot_SP=snapshot['registers'][SP],
                  snapshot_IFF=snapshot['registers'][26], snapshot_IM=snapshot['registers'][27],
                  profiles_with_enabled_IFF=sum(bool(case['enabled_iff_steps']) for case in cases),
                  enabled_IFF_positions=[dict(bank=bank, PC=pc, observations=count)
                                         for (bank, pc), count in sorted(enabled_iff_positions.items())],
                  handler_dispatch_totals={f'{target:04X}': count for target, count in sorted(dispatch_totals.items())},
                  all_selected_handlers_returned=True, scanner_SP_restored=True,
                  temporary_module_entries=0, watched_control_source_or_length_writes=0,
                  fixed_RAM_module_window_writes=0,
                  all_larger_chords_or_game_states_exhausted=False,
                  natural_temporary_module_entry_proved=False,
                  keyboard_response_only_during_scanner=True, IRQ_executed_during_scan=False,
                  keyboard_electrical_ghosting_modelled=False,
                  boot_TRDOS_stub=True, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FlightKeyChordsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'profiles'}, indent=2))


if __name__ == '__main__':
    main()
