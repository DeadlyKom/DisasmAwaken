"""Два входа обхода неактивных записей, двойной маркер, R и отсутствие записей.

Документация: ../../../Docs/ActionObjectWalk.md#неактивные-записи-и-два-входа
"""
from hashlib import sha256
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckMusicGateTicks import Memory
from CheckStationFlightCycle import DISK, ENTRIES, ROOT
from ReferenceControlsPointRespawn import refresh
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, IXh, IXl, get_registers


def main():
    baseline = flat_action()
    code = bytes(baseline[0xF729:0xF792])
    offset = ENTRIES[17]['offset'] + 0x9729
    assert code == DISK[offset:offset + len(code)]
    memory = Memory(baseline)
    memory[0xBFFE:0xC000] = [255, 63]
    cpu = Simulator(memory)
    total = 0
    formulas = {}
    for entry, slots, initial_r in product((0xF729, 0xF735), range(26), range(256)):
        records = bytearray([0xA5] * (26 * 64))
        for index in range(slots):
            value = (index * 37 + initial_r) & 255
            records[index * 64] = 0x81 if value == 0x80 else value
            records[index * 64 + 1] = 0x80
            # Недопустимый код состояния обнаружил бы ошибочный заход в активную обработку.
            records[index * 64 + 10] = 0xFF
        marker = 0xA100 + 64 * slots
        records[slots * 64:slots * 64 + 2] = bytes((0x80, 0x80))
        memory[0xA100:0xA780] = records
        initial = get_registers(dict(PC=entry, SP=0xBFFE, R=initial_r,
            HL=0x1357, DE=0x2468, BC=0x369C, AF=0x5A96, IX=0xA0C0, IY=0xABCD, I=0x3C,
            **{'^HL':0x47AD, '^DE':0x58BE, '^BC':0x69CF, '^AF':0x7AD0}), {'im':2, 'iff':0}, False)
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        m1 = 0
        for _ in range(256):
            pc = cpu.registers[PC]
            if pc == 0x3FFF:
                break
            assert 0xF729 <= pc < 0xF742, (entry, slots, initial_r, pc)
            opcode = memory[pc]
            assert opcode not in (0xCB, 0xED, 0xFD)
            m1 += 2 if opcode == 0xDD else 1
            cpu.run()
            assert cpu.registers[R] == refresh(initial_r, m1)
        else:
            raise AssertionError(('inactive_walk_instruction_limit', entry, slots))
        memory.recording = False
        expected_m1 = 11 * (slots + 1) + (3 if entry == 0xF729 else 0)
        r = cpu.registers
        assert m1 == expected_m1 and r[PC] == 0x3FFF and r[SP] == 0xC000
        assert r[IXh] * 256 + r[IXl] == marker and r[:2] == [0x80, 0x42] and r[4:6] == [0, 64]
        assert all(r[i] == initial[i] for i in (2, 3, 6, 7, 10, 11, 14, *range(16, 24), 26, 27))
        assert not memory.writes and bytes(memory[0xA100:0xA780]) == records
        formulas[entry, slots] = expected_m1
        total += 1
    # Проверка ложного маркера, первый байт 80 без второго 80 обязан выбрать активный путь.
    memory[0xA100:0xA140] = bytes(64)
    memory[0xA100] = 0x80
    memory[0xA112] = 0x10
    cpu.registers[:] = get_registers(dict(PC=0xF729, SP=0xBFFE), {'im':2, 'iff':0}, False)
    memory.writes = []
    memory.recording = True
    for _ in range(32):
        if cpu.registers[PC] in (0xF843, 0x3FFF):
            break
        cpu.run()
    memory.recording = False
    assert cpu.registers[PC] == 0xF843 and cpu.registers[SP] == 0xBFFE
    assert cpu.registers[IXh] * 256 + cpu.registers[IXl] == 0xA100 and not memory.writes
    report = dict(passed=True, inactive_cases=total, original_code_sha256=sha256(code).hexdigest(),
                  entries=[0xF729, 0xF735], inactive_record_counts=list(range(26)),
                  all_R_values_crossed_with_both_entries_and_every_count=True,
                  exact_M1_formulas=[dict(entry=entry, inactive_records=count, M1=value)
                                     for (entry, count), value in sorted(formulas.items())],
                  registers_and_all_record_bytes_compared=True, no_memory_writes=True,
                  no_handler_or_scale_calls=True, double_byte_marker_required=True,
                  single_80_probe_stopped_at_real_CallHandler=True,
                  active_handlers_executed=False, IRQ_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionInactiveObjectWalkVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены 13312 неактивных проходов, два входа, все R и ложный однобайтовый маркер.')


if __name__ == '__main__':
    main()
