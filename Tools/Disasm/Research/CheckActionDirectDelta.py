"""Прямой вход 638C со всеми байтами поправки, включая переполнение добавки.

Документация: ../../../Docs/ActionTypeDelta.md#прямой-вход-adjustmode
"""
from collections import Counter
from hashlib import sha256
import json

from CheckActionParameterActivation import flat_action
from CheckActionTypeDelta import cp_flags, signed
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from CheckStationFlightCycle import DISK, ENTRIES
from ClassifyControlsTextDisplay import ROOT


def main():
    original = flat_action()
    code = bytes(original[0x638C:0x63B6])
    offset = ENTRIES[17]['offset'] + 0x5C9
    assert code == DISK[offset:offset + len(code)]
    memory = Memory(original)
    expected = list(memory)
    cpu = Simulator(memory)
    counts = Counter()
    wrapped = 0

    def check(delta, mode, old, kind):
        nonlocal wrapped
        serial = counts.total()
        memory.recording = False
        memory[0x9B83], memory[0x9BCD] = mode, old
        expected[0x9B83], expected[0x9BCD] = mode, old
        memory[0xBFFE:0xC000] = expected[0xBFFE:0xC000] = [255,63]
        initial = get_registers(dict(PC=0x638C, SP=0xBFFE, AF=serial & 65535,
            HL=0x1357, DE=0x2468, BC=0xA500 | delta, IX=0xABCD, IY=0x5C3A,
            I=serial & 255, R=serial & 255,
            **{'^AF':0xDEF0, '^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC}),
            {'im':serial % 3, 'iff':serial & 1}, False)
        # Расчёт эффективной знаковой поправки, добавка сама ограничивается байтом.
        boost = bool(mode and delta < 128)
        effective_byte = (delta + (10 if boost else 0)) & 255
        effective = signed(effective_byte)
        total = signed(old) + effective
        result = max(0, min(127, total)) | (32 if old < 32 else 0)
        overflow = not -128 <= total <= 127
        negative = old >= 128 if overflow else total < 0
        m1 = 15 + (5 if boost else 3 if mode else 0) + 2 * overflow + negative + 2 * (old < 32)
        wanted = list(initial)
        wanted[:4] = [result, cp_flags(old,32), old, result]
        wanted[SP], wanted[PC], wanted[15] = 0xC000, 0x3FFF, refresh(initial[15],m1)
        expected[0x9BCD] = result
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        cpu.run(0x638C, 0x3FFF)
        memory.recording = False
        # Проверка регистров вместе с R, всей RAM и единственной записи состояния.
        compared = (*range(13), 14, 15, *range(16,25), 26, 27)
        assert all(cpu.registers[i] == wanted[i] for i in compared), (delta,mode,old)
        assert memory == expected and memory.writes == [(0x9BCD,result)], (delta,mode,old)
        wrapped += int(boost and delta >= 118)
        counts[kind] += 1

    # Проверка всех исходных состояний и поправок в обоих классах режима.
    for mode in (0,1):
        for delta in range(256):
            for old in range(256):
                check(delta,mode,old,'all_delta_and_state_bytes_two_mode_classes')
    # Проверка всех кодов режима для двух реально передаваемых непосредственных поправок.
    for delta in (8,32):
        for mode in range(256):
            for old in (0,31,32,117,127,128,255):
                check(delta,mode,old,'actual_call_deltas_all_mode_bytes')
    report = dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
                  original_direct_entry_sha256=sha256(code).hexdigest(),
                  boost_wrap_cases=wrapped, boost_wrap_input_bytes=list(range(118,128)),
                  exact_registers_flags_R_SP_and_all_RAM_compared=True,
                  single_state_write_and_no_CPU_stack_writes=True,
                  actual_call_deltas=[8,32], all_joint_mode_delta_state_inputs_exhausted=False,
                  game_meaning_of_state_and_mode_proved=False,
                  IRQ_executed=False,assembly_executed=False,native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionDirectDeltaVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
