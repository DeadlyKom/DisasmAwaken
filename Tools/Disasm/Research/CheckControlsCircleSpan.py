"""Самостоятельный D320, оба настоящих построителя маски и каждый байт побочных записей."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost


def add_flags(a, b):
    value = (a+b)&255
    return ((value&0xA8) | (0x40 if value == 0 else 0)
            | (0x10 if (a&15)+(b&15)>15 else 0)
            | (4 if (~(a^b)&(a^value)&128) else 0) | int(a+b>255))


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()

    def check(radius, cx, cy, flags, kind):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0xD17F:0xD181] = [flags, radius]
        memory[0xD183:0xD185] = [cy, cx]
        memory[0xBFFE:0xC000] = [0xFF, 0x3F]
        initial = get_registers({'AF': 0xA55A, 'HL': 0x1357, 'DE': 0x2468,
            'BC': 0x369C, '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678,
            '^BC': 0x9ABC, 'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xD320}, None, False)
        initial[14], initial[15], initial[26], initial[27] = flags, (cx+cy)&255, radius&1, cx%3
        left, right = (cx-radius)&255, (cx+radius)&255
        left_address = 0x8000+32*cy+left//8
        right_address = 0x8000+32*cy+right//8
        left_mask = (255 << (7-(left&7)))&255
        right_mask = 255 >> (right&7)
        wanted = list(initial)
        wanted[0:8] = [left_mask, 0x42, left_mask, right_mask,
                       radius, left_address&255, right_address>>8, right_address&255]
        wanted[19], wanted[21] = (-radius)&255, 0
        wanted[SP] = 0xC000
        # Расчёт M1 по двум длинам масок и одному прямому пути подготовителя.
        cost = (block_cost(0xD320, 0xD340)+block_cost(0xD515, 0xD532)
                +(1+(left&7))*block_cost(0xD532, 0xD537)+block_cost(0xD537, 0xD53C)
                +block_cost(0xD53C, 0xD562)+(8-(right&7))*block_cost(0xD562, 0xD567)
                +block_cost(0xD567, 0xD56C))
        wanted[15] = refresh(initial[15], cost)
        writes = [(0xBFFD, 0xD3), (0xBFFC, 0x35), (0xBFFD, right),
                  (0xBFFC, add_flags(cx, radius)), (0xD18A, left_mask)]
        expected = list(memory)
        for address, value in writes:
            expected[address] = value
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(160):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат', radius, cx, cy))
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (radius, cx, cy,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert memory == expected and Counter(memory.writes) == Counter(writes), (radius, cx, cy,
            memory.writes, writes, [(i, a, b) for i, (a, b) in enumerate(zip(memory, expected)) if a != b][:8])
        touched = {address for address, _ in writes}
        counts[kind] += 1

    # Проверка всех пар радиуса и X, байтовые переносы не исключаются.
    for radius in range(256):
        for cx in range(256):
            check(radius, cx, (radius+31*cx)&255, (radius*73+cx)&255, 'radius_x')
        if radius%64 == 63:
            print('Circle span radii', radius+1, flush=True)
    # Проверка каждой пары строки и X независимо от первого набора.
    for cy in range(256):
        for cx in range(256):
            check(9, cx, cy, (cy+cx)&255, 'row_x')
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_kind=dict(counts),
        original_tail_jump_returns_to_external_caller=True, real_mask_helpers_without_stubs=True,
        every_ram_byte_and_write_checked=True, exact_registers_flags_r_and_sp=True,
        remaining_d340_branches_proved=False, whole_large_renderer_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleSpanVerification.json').write_bytes(
        (json.dumps(report, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
