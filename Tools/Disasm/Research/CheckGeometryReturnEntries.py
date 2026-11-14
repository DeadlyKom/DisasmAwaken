"""Исходные четыре выхода геометрии, кадры, точный R и собственные записи RAM.

Документация: ../../../Docs/TrackGeometry.md#общие-выходы-и-стек
"""
from hashlib import sha256
import json
from CheckTrackGeometry import ROOT, Simulator, get_registers, and_flags


class Memory(bytearray):
    recording = False

    def __init__(self, size):
        super().__init__(size)
        self.writes = []

    def __setitem__(self, index, value):
        if self.recording:
            assert isinstance(index, int)
            self.writes.append((index, value))
        super().__setitem__(index, value)


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(row for row in manifest['entries'] if row['slot'] == 4)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    assert len(source) == entry['allocated_length']
    assert disk[entry['offset']:entry['offset'] + len(source)] == source
    # Проверка наблюдателя настоящей записью CPU в отдельную память.
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex('320070')
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(65536)
    memory[0x6000:0x6000 + len(source)] = source
    # Проверка всего общего хвоста по исходным байтам, а не только адресам входа.
    body = bytes(memory[0xCA04:0xCA1F])
    assert body == bytes.fromhex('af32829ac1d1e1f1dde1a737c9c1c118efc1c1c1d1e1f1dde1a7c9')
    cpu = Simulator(memory)
    initial = get_registers({'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, 'AF': 0x47AD,
        '^HL': 0x5678, '^DE': 0x6789, '^BC': 0x789A, '^AF': 0x89AB,
        'IX': 0x9ABC, 'IY': 0xABCD, 'SP': 0x7FF0}, None, False)
    cases = {}
    entries = ((0xCA04, 'finish', False, True, 11), (0xCA11, 'mark', True, True, 14),
               (0xCA15, 'cancel_hit', True, False, 10), (0xCA17, 'return', False, False, 8))
    for address, name, nested, success, cost in entries:
        cases[name] = 0
        for saved_a in range(256):
            for refresh in range(256):
                seed = (saved_a << 8) | refresh
                saved = (seed ^ 0x1357, seed ^ 0x2468, seed ^ 0x369C,
                         (saved_a << 8) | (saved_a ^ refresh), seed ^ 0xABCD)
                words = ((seed ^ 0x48AE, seed ^ 0x59BF) if nested else ()) + saved + (0x3FFF,)
                frame = b''.join(word.to_bytes(2, 'little') for word in words)
                frame_start = 0x8000 - len(frame)
                memory[frame_start:0x8000] = frame
                memory[0x9A82] = 0xA5
                expected = list(initial)
                expected[14], expected[15] = saved_a, refresh
                expected[26], expected[27] = refresh & 1, saved_a % 3
                expected[12], expected[24] = frame_start, address
                cpu.registers[:] = expected
                memory.writes.clear()
                memory.recording = True
                cpu.run(address, 0x3FFF)
                memory.recording = False
                # Расчёт результата снятия BC, DE, HL, AF и IX из физического кадра.
                for low, high, word in ((3, 2, saved[0]), (5, 4, saved[1]),
                                        (7, 6, saved[2]), (9, 8, saved[4])):
                    expected[low], expected[high] = word & 255, word >> 8
                expected[0] = saved_a
                expected[1] = ((and_flags(saved_a) & 0xC4) | (saved_a & 0x28) | 1
                               if success else and_flags(saved_a))
                expected[12], expected[24] = 0x8000, 0x3FFF
                expected[15] = (refresh & 0x80) | ((refresh + cost) & 0x7F)
                assert all(cpu.registers[i] == expected[i] for i in range(len(expected)) if i != 25), (name, seed)
                assert memory.writes == ([(0x9A82, 0)] if success else []), (name, seed, memory.writes)
                assert memory[0x9A82] == (0 if success else 0xA5)
                assert bytes(memory[frame_start:0x8000]) == frame
                cases[name] += 1
    report = dict(passed=True, method='original_geometry_return_entries_against_explicit_frames_and_RAM_write_watch',
        cases=sum(cases.values()), cases_by_entry=cases, original_disk_sha256=sha256(disk).hexdigest(),
        original_common_tail_sha256=sha256(body).hexdigest(), all_saved_A_and_initial_R_pairs=True,
        all_saved_AF_values_covered=True, saved_AF_and_R_full_joint_product=False,
        exact_registers_except_T_checked=True, R_bit7_preserved=True,
        M1_by_entry={name:cost for _, name, _, _, cost in entries},
        SP_delta_by_entry={name:16 if nested else 12 for _, name, nested, _, _ in entries},
        only_own_RAM_write_is_EventEnabled_zero_on_success=True, CPU_write_watch_positive_control=True,
        frame_bytes_unchanged=True, no_own_stack_writes=True, arbitrary_frame_addresses_or_overlaps_checked=False,
        MarkGeometry_current_caller_proved=False, input_hardware_or_ISR_executed=False,
        assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/GeometryReturnEntriesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('passed', 'cases', 'M1_by_entry', 'SP_delta_by_entry')}))


if __name__ == '__main__':
    main()
