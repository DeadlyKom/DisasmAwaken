"""Преобразование двух координат E4FC..E52A, без фильтра записей и без рисования объектов."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh, cp_flags
from ReferenceControlsPointMotion import block_cost


def scale(value):
    signed = value if value < 128 else value - 256
    quarter = signed // 4
    return quarter + (quarter + 1) // 2


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    counts = Counter()
    for raw_x in range(256):
        for raw_z in range(256):
            initial = get_registers({'AF': 0xA55A, 'HL': 0x1357, 'DE': 0x4000 | raw_z,
                'BC': 0x3600 | raw_x, '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678,
                '^BC': 0x9ABC, 'IX': 0xA100, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xE4FC}, None, False)
            initial[14], initial[15], initial[26], initial[27] = raw_x, raw_z, raw_x & 1, raw_z % 3
            sx, sy = scale(raw_x), scale((-raw_z) & 255)
            y, x = (144 + sy) & 255, (104 + sx) & 255
            wanted = list(initial)
            wanted[3], wanted[5], wanted[0] = sy & 255, sx & 255, y
            wanted[PC] = 0xE4B7
            m1 = block_cost(0xE4FC, 0xE51A)
            if y >= 181:
                boundary, operand = 'y_upper', 181
            elif y < 107:
                boundary, operand = 'y_lower', 107
                m1 += block_cost(0xE51A, 0xE51E)
            else:
                wanted[3], wanted[0] = y, x
                m1 += block_cost(0xE51A, 0xE526)
                if x >= 141:
                    boundary, operand = 'x_upper', 141
                elif x < 64:
                    boundary, operand = 'x_lower', 64
                    m1 += block_cost(0xE526, 0xE52A)
                else:
                    boundary, operand = 'accepted', 64
                    wanted[5], wanted[PC] = x, 0xE52B
                    m1 += block_cost(0xE526, 0xE52B)
            wanted[1] = cp_flags(wanted[0], operand)
            wanted[15] = refresh(initial[15], m1)
            simulator.registers[:] = initial
            memory.writes = []
            memory.recording = True
            for _ in range(40):
                if simulator.registers[PC] == wanted[PC]:
                    break
                simulator.run()
            else:
                raise AssertionError(('граница', raw_x, raw_z, simulator.registers[PC]))
            memory.recording = False
            compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
            assert all(wanted[i] == simulator.registers[i] for i in compared), (raw_x, raw_z, boundary,
                [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
            assert memory == original and memory.writes == []
            counts[boundary] += 1
    report = dict(passed=True, total_cases=counts.total(), cases_by_path=dict(counts),
        all_raw_x_z_pairs=True, exact_registers_flags_refresh_sp=True,
        every_ram_byte_checked=True, no_memory_writes=True,
        accepted_screen_x=[64, 140], accepted_screen_y=[107, 180],
        raw_80_rejected_by_caller=True, direct_entry_80_also_checked=True,
        object_record_filter_proved=False, height_stem_proved=False, icon_drawing_proved=False,
        full_e291_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsObjectProjectionVerification.json').write_bytes(
        (json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
